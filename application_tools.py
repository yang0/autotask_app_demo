import aiohttp
import asyncio
from typing import Dict, Any, Optional
from loguru import logger
from datetime import datetime

class ToolsClient:
    def __init__(self, base_url: str = "http://localhost:8283"):
        self._node_api_base = base_url
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()

    async def _ensure_session(self):
        """Ensure HTTP session is created"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            
    async def close_session(self):
        """Close HTTP session if exists"""
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def run_node(self, class_path: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a node via HTTP API
        
        Args:
            class_path: Node class path
            inputs: Node input parameters
            
        Returns:
            Node execution result
        """
        await self._ensure_session()
        
        try:
            url = f"{self._node_api_base}/nodes/execute/{class_path}"
            
            logger.debug(f"Executing node {class_path} with inputs: {inputs}")
            
            async with self._session.post(url, json=inputs) as response:
                response.raise_for_status()
                result = await response.json()
                logger.debug(f"Node {class_path} execution result: {result}")
                return result
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error executing node {class_path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error executing node {class_path}: {str(e)}")
            raise

    async def get_node_info(self, class_path: str) -> Dict[str, Any]:
        """Get node information via HTTP API
        
        Args:
            class_path: Node class path
            
        Returns:
            Node information including inputs and outputs
        """
        await self._ensure_session()
        
        try:
            url = f"{self._node_api_base}/nodes/nodes/{class_path}"
            
            async with self._session.get(url) as response:
                response.raise_for_status()
                info = await response.json()
                logger.debug(f"Retrieved info for node {class_path}: {info}")
                return info
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error getting node info for {class_path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting node info for {class_path}: {str(e)}")
            raise

    async def list_nodes(self, category: Optional[str] = None) -> Dict[str, Any]:
        """List available nodes via HTTP API
        
        Args:
            category: Optional category to filter nodes
            
        Returns:
            List of available nodes
        """
        await self._ensure_session()
        
        try:
            url = f"{self._node_api_base}/nodes/nodes"
            if category:
                url += f"?category={category}"
                
            async with self._session.get(url) as response:
                response.raise_for_status()
                nodes = await response.json()
                logger.debug(f"Retrieved nodes list: {len(nodes)} nodes")
                return nodes
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error listing nodes: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error listing nodes: {str(e)}")
            raise

    async def run_workflow(self, workflow_uuid: str) -> Dict[str, Any]:
        """Execute a workflow synchronously via HTTP API
        
        Args:
            workflow_uuid: UUID of the workflow to execute
            
        Returns:
            Workflow execution result
        """
        await self._ensure_session()
        
        try:
            url = f"{self._node_api_base}/run_workflow_sync/{workflow_uuid}"
            
            async with self._session.post(url) as response:
                response.raise_for_status()
                result = await response.json()
                logger.debug(f"Workflow {workflow_uuid} execution result: {result}")
                return result
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error executing workflow {workflow_uuid}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_uuid}: {str(e)}")
            raise

    async def run_assistant_sync(
        self,
        assistant_id: str,
        message: str,
        session_id: Optional[str] = None,
        message_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute an assistant synchronously via HTTP API
        
        Args:
            assistant_id: ID of the assistant to execute
            message: Message to send to the assistant
            session_id: Optional session ID for conversation context
            message_type: Optional message type
            metadata: Optional metadata for the request
            
        Returns:
            Assistant execution result containing response content
        """
        await self._ensure_session()
        
        try:
            url = f"{self._node_api_base}/assistant/run_sync"
            
            data = {
                "assistant_id": assistant_id,
                "message": message,
                "session_id": session_id,
                "message_type": message_type,
                "metadata": metadata
            }
            
            logger.debug(f"Executing assistant {assistant_id} with message: {message}")
            
            async with self._session.post(url, json=data) as response:
                response.raise_for_status()
                result = await response.json()
                logger.debug(f"Assistant {assistant_id} execution result: {result}")
                return result
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error executing assistant {assistant_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error executing assistant {assistant_id}: {str(e)}")
            raise

    def run_node_sync(self, class_path: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous version of run_node"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._run_node_sync(class_path, inputs))
        finally:
            loop.close()

    async def _run_node_sync(self, class_path: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Internal async method for run_node_sync"""
        async with aiohttp.ClientSession() as session:
            url = f"{self._node_api_base}/nodes/execute/{class_path}"
            
            logger.debug(f"Executing node {class_path} with inputs: {inputs}")
            
            async with session.post(url, json=inputs) as response:
                response.raise_for_status()
                result = await response.json()
                logger.debug(f"Node {class_path} execution result: {result}")
                return result

    