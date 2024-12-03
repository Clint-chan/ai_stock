# tools/utils/kernel_utils.py

import os
import sys
import subprocess
import uuid
import time
import queue
import signal
import atexit
import json
from jupyter_client import BlockingKernelClient, launch_kernel
from typing import Dict, Optional, Tuple,Any

def append_signal_handler(sig, handler):
    """
    安装新的信号处理器,同时保留现有处理器。
    如果存在现有处理器,它将在新处理器之后被调用。
    """
    old_handler = signal.getsignal(sig)
    if not callable(old_handler):
        old_handler = None
        if sig == signal.SIGINT:
            def old_handler(*args, **kwargs):
                raise KeyboardInterrupt
        elif sig == signal.SIGTERM:
            def old_handler(*args, **kwargs):
                raise SystemExit

    def new_handler(*args, **kwargs):
        handler(*args, **kwargs)
        if old_handler is not None:
            old_handler(*args, **kwargs)

    signal.signal(sig, new_handler)

# 全局变量存储kernel客户端和子进程
_KERNEL_CLIENTS: dict = {}
_MISC_SUBPROCESSES: Dict[str, subprocess.Popen] = {}

def _kill_kernels_and_subprocesses(_sig_num=None, _frame=None):
    """清理所有kernel和子进程"""
    for v in _KERNEL_CLIENTS.values():
        v.shutdown()
    for k in list(_KERNEL_CLIENTS.keys()):
        del _KERNEL_CLIENTS[k]

    for v in _MISC_SUBPROCESSES.values():
        v.terminate()
    for k in list(_MISC_SUBPROCESSES.keys()):
        del _MISC_SUBPROCESSES[k]

# 确保程序退出时清理资源
atexit.register(_kill_kernels_and_subprocesses)
append_signal_handler(signal.SIGTERM, _kill_kernels_and_subprocesses)
append_signal_handler(signal.SIGINT, _kill_kernels_and_subprocesses)


class KernelManager:
    """Jupyter内核管理器"""

    def __init__(self):
        self.work_dir = os.path.join(os.path.dirname(__file__), "../workspace")
        os.makedirs(self.work_dir, exist_ok=True)
        self.instance_id = str(uuid.uuid4())
        self.kernel_id = f'{self.instance_id}_{os.getpid()}'

    def execute(self, code: str, timeout: Optional[int] = 30) -> str:
        """执行代码并获取结果"""
        if self.kernel_id in _KERNEL_CLIENTS:
            kc = _KERNEL_CLIENTS[self.kernel_id]
        else:
            kc, km = self._start_kernel()
            _KERNEL_CLIENTS[self.kernel_id] = kc
            _MISC_SUBPROCESSES[self.kernel_id] = km

        kc.execute(code)
        result = ""

        start_time = time.time()
        while True:
            try:
                if timeout and time.time() - start_time > timeout:
                    return "执行超时"

                msg = kc.get_iopub_msg(timeout=1)
                msg_type = msg['msg_type']

                if msg_type == 'execute_result':
                    result += msg['content']['data'].get('text/plain', '')
                elif msg_type == 'stream':
                    result += msg['content']['text']
                elif msg_type == 'error':
                    result += '\n'.join(msg['content']['traceback'])
                elif msg_type == 'status':
                    if msg['content']['execution_state'] == 'idle':
                        break

            except queue.Empty:
                continue
            except Exception as e:
                result += f"\n执行出错: {str(e)}"
                break

        return result.strip()

    def _start_kernel(self) -> Tuple[BlockingKernelClient, Any]:
        """启动Jupyter内核"""
        connection_file = os.path.join(self.work_dir, f'kernel_connection_file_{self.kernel_id}.json')
        launch_kernel_script = os.path.join(self.work_dir, f'launch_kernel_{self.kernel_id}.py')

        # 清理已存在的文件
        for f in [connection_file, launch_kernel_script]:
            if os.path.exists(f):
                os.remove(f)

        # 创建启动脚本 - 注意这里去掉了多余的缩进
        with open(launch_kernel_script, 'w') as fout:
            fout.write('from ipykernel import kernelapp as app\n')
            fout.write('app.launch_new_instance()\n')

        # 启动内核进程
        kernel_process = subprocess.Popen(
            [
                sys.executable,
                os.path.abspath(launch_kernel_script),
                '--IPKernelApp.connection_file',
                os.path.abspath(connection_file),
                '--matplotlib=inline',
                '--quiet',
            ],
            cwd=os.path.abspath(self.work_dir),
        )

        # 等待连接文件创建完成
        while True:
            if not os.path.isfile(connection_file):
                time.sleep(0.1)
            else:
                try:
                    with open(connection_file, 'r') as fp:
                        json.load(fp)
                    break
                except json.JSONDecodeError:
                    pass

        # 创建客户端
        kc = BlockingKernelClient(connection_file=connection_file)
        kc.load_connection_file()
        kc.start_channels()
        kc.wait_for_ready()

        return kc, kernel_process

    def cleanup(self):
        """清理单个内核的资源"""
        if self.kernel_id in _KERNEL_CLIENTS:
            _KERNEL_CLIENTS[self.kernel_id].shutdown()
            del _KERNEL_CLIENTS[self.kernel_id]
        if self.kernel_id in _MISC_SUBPROCESSES:
            _MISC_SUBPROCESSES[self.kernel_id].terminate()
            del _MISC_SUBPROCESSES[self.kernel_id]
