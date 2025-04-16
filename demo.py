import os
import sys
import logging
from typing import Dict, Any, Optional

# 设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 打印环境调试信息
logger.info("=== Demo Module Debug Info ===")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python executable: {sys.executable}")
logger.info("Python path:")
for p in sys.path:
    logger.info(f"  - {p}")
logger.info("Environment PATH:")
for p in os.environ.get('PATH', '').split(os.pathsep):
    logger.info(f"  - {p}")

# 检查 tornado 包位置
try:
    import tornado
    logger.info(f"Tornado package location: {tornado.__file__}")
    
    # 检查 tornado 包目录内容
    tornado_dir = os.path.dirname(tornado.__file__)
    logger.info(f"Tornado directory contents:")
    for root, dirs, files in os.walk(tornado_dir):
        rel_path = os.path.relpath(root, tornado_dir)
        if rel_path == '.':
            logger.info(f"  Files in root:")
        else:
            logger.info(f"  Files in {rel_path}:")
        for f in files:
            logger.info(f"    - {f}")
        for d in dirs:
            logger.info(f"    [dir] {d}")

    # 尝试直接检查 websocket.py 是否存在
    websocket_path = os.path.join(tornado_dir, 'websocket.py')
    websocket_pyc_path = os.path.join(tornado_dir, 'websocket.pyc')
    logger.info(f"Checking websocket.py: exists={os.path.exists(websocket_path)}")
    logger.info(f"Checking websocket.pyc: exists={os.path.exists(websocket_pyc_path)}")

except Exception as e:
    logger.error(f"Failed to import tornado: {e}")
    logger.error("Detailed error:", exc_info=True)

# 现在尝试导入 streamlit
import streamlit.web.cli as stcli
from autotask.application.base_application import BaseApplication, ConfigField
from autotask.application.application_registry import register_application
import multiprocessing
import signal

# Global instance variable for the current process
_current_instance = None
_streamlit_process = None

def run_streamlit(port: int):
    """Run streamlit application"""
    try:
        # 打印调试信息
        logger.info("=== Streamlit Process Debug Info ===")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Python executable: {sys.executable}")
        logger.info("Python path:")
        for p in sys.path:
            logger.info(f"  - {p}")
        logger.info("Environment PATH:")
        for p in os.environ.get('PATH', '').split(os.pathsep):
            logger.info(f"  - {p}")
        
        # 检查 tornado 包位置
        try:
            import tornado
            logger.info(f"Tornado package location: {tornado.__file__}")
        except Exception as e:
            logger.error(f"Failed to import tornado: {e}")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        streamlit_file = os.path.join(current_dir, "streamlit_ui.py")
        
        # Set up command line arguments for Streamlit
        sys.argv = [
            "streamlit",
            "run",
            streamlit_file,
            "--server.port", str(port),
            "--server.address", "0.0.0.0",
            "--browser.serverAddress", "localhost",
            "--global.developmentMode", "false",
            "--logger.level", "info",
            "--server.runOnSave", "false"
        ]
        
        # Run Streamlit using CLI
        stcli.main()
    except Exception as e:
        logger.error(f"Error running Streamlit: {str(e)}")
        raise

@register_application()
class AutotaskApplicationDemo(BaseApplication):
    name = "File Browser Demo"
    description = "A demo application for browsing files using Streamlit"
    
    @classmethod
    def get_config_schema(cls) -> Dict[str, ConfigField]:
        return {
                "port": ConfigField(
                    field_type="number",
                    label="Port Number",
                    description="Port to run the application on",
                    default=8501,
                    required=True,
                    section="server"
                )
            }

    
    def __init__(self, config: Dict[str, Any]={}):
        super().__init__(config)
        self.port = config.get("port", 8501)
        # Set the global instance for this process
        global _current_instance
        _current_instance = self

    async def start(self):
        """Start the demo application."""
        logger.info("Starting File Browser Demo")
        try:
            global _streamlit_process
            # Create and start streamlit in a separate process
            _streamlit_process = multiprocessing.Process(target=run_streamlit, args=(self.port,), daemon=True)
            _streamlit_process.start()
            logger.info(f"Streamlit process started on port {self.port} with PID {_streamlit_process.pid}")
        except Exception as e:
            logger.error(f"Failed to start Streamlit: {str(e)}")
            raise
        
    async def stop(self):
        """Stop the demo application."""
        logger.info("Stopping File Browser Demo")
        try:
            # Stop streamlit process if running
            global _streamlit_process
            if _streamlit_process and _streamlit_process.is_alive():
                _streamlit_process.terminate()
                _streamlit_process.join(timeout=5)
                if _streamlit_process.is_alive():
                    _streamlit_process.kill()  # Force kill if still alive
                _streamlit_process = None
        finally:
            global _current_instance
            _current_instance = None

def get_current_instance() -> Optional[AutotaskApplicationDemo]:
    """Get the current instance in this process."""
    return _current_instance

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create and start the demo
    demo = AutotaskApplicationDemo()
    import asyncio
    asyncio.run(demo.start())
    
    # Keep the main process running
    try:
        while True:
            if _streamlit_process and not _streamlit_process.is_alive():
                break
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        asyncio.run(demo.stop())

