import asyncio
from concurrent.futures import ThreadPoolExecutor
import structlog
import uuid
from typing import Dict, Optional, Any
import time
from prometheus_client import Histogram

# Initialize logging
logger = structlog.get_logger()

# Metrics
QUEUE_TIME = Histogram('ocr_queue_time_seconds', 'Time spent in queue')
PROCESSING_TIME = Histogram('ocr_processing_time_seconds', 'Time spent processing')

# Initialize test metrics
TEST_QUEUE_TIME = Histogram('test_ocr_queue_time_seconds', 'Time spent in test queue')
TEST_PROCESSING_TIME = Histogram('test_ocr_processing_time_seconds', 'Time spent processing in test mode')

class OCRPipeline:
    def __init__(self, model_manager, max_workers: int = 4, queue_size: int = 10):
        """Initialize OCR pipeline with hybrid model manager"""
        self.model_manager = model_manager
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.queue_size = queue_size
        self.processing = True
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.test_tasks: Dict[str, Dict[str, Any]] = {}  # Separate storage for test tasks
        self.queue = asyncio.Queue(maxsize=queue_size)
        self.test_queue = asyncio.Queue(maxsize=queue_size)  # Separate queue for test tasks
        self.processing_task = asyncio.create_task(self._process_queue())
        self.test_processing_task = asyncio.create_task(self._test_process_queue())
        logger.info("Pipeline initialized", 
                   max_workers=max_workers, 
                   queue_size=queue_size)

    async def process_image(self, image_data: bytes, engine: Optional[str] = None, language: str = "en") -> str:
        """Queue image for processing with specified engine preference"""
        if not self.processing:
            raise RuntimeError("Pipeline is shutting down")
        
        task_id = str(uuid.uuid4())
        enqueue_time = time.time()
        
        await self.queue.put({
            "task_id": task_id,
            "image_data": image_data,
            "engine": engine,
            "language": language,
            "enqueue_time": enqueue_time
        })
        
        self.tasks[task_id] = {
            "status": "processing",
            "enqueue_time": enqueue_time
        }
        
        logger.info("Task queued", 
                   task_id=task_id,
                   queue_size=self.queue.qsize(),
                   engine=engine,
                   language=language)
        
        return task_id

    def get_result(self, task_id: str) -> Optional[Dict]:
        """Get result for task ID"""
        return self.tasks.get(task_id)

    async def _process_queue(self):
        """Process queued images"""
        while self.processing:
            try:
                task = await self.queue.get()
                task_id = task["task_id"]
                
                # Calculate queue time
                queue_time = time.time() - task["enqueue_time"]
                QUEUE_TIME.observe(queue_time)
                
                logger.info("Processing task", 
                           task_id=task_id,
                           queue_time=queue_time)
                
                # Process in thread pool
                start_time = time.time()
                try:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        self.executor,
                        self._process_task,
                        task
                    )
                    
                    processing_time = time.time() - start_time
                    PROCESSING_TIME.observe(processing_time)
                    
                    self.tasks[task_id].update({
                        "status": "completed",
                        "result": result,
                        "processing_time": processing_time,
                        "queue_time": queue_time
                    })
                    
                    logger.info("Task completed", 
                              task_id=task_id,
                              processing_time=processing_time)
                    
                except Exception as e:
                    logger.error("Task failed", 
                               task_id=task_id,
                               error=str(e))
                    self.tasks[task_id].update({
                        "status": "failed",
                        "error": str(e)
                    })
                
                finally:
                    self.queue.task_done()
                
            except Exception as e:
                logger.error("Queue processing error", error=str(e))
                await asyncio.sleep(1)  # Prevent tight loop on persistent errors

    def _process_task(self, task: Dict) -> Dict:
        """Process single OCR task"""
        return self.model_manager.process_image(
            task["image_data"],
            engine=task["engine"],
            language=task["language"]
        )

    async def shutdown(self):
        """Shutdown pipeline"""
        logger.info("Shutting down pipeline")
        self.processing = False
        
        # Wait for queue to empty
        if not self.queue.empty():
            await self.queue.join()
        
        # Cancel processing task
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        # Shutdown thread pool
        self.executor.shutdown(wait=True)
        logger.info("Pipeline shutdown complete")

    async def test_process_image(self, image_data: bytes, engine: Optional[str] = None, language: str = "en") -> str:
        """Queue image for processing in test mode"""
        if not self.processing:
            raise RuntimeError("Pipeline is shutting down")
        
        task_id = f"test_{str(uuid.uuid4())}"
        enqueue_time = time.time()
        
        await self.test_queue.put({
            "task_id": task_id,
            "image_data": image_data,
            "engine": engine,
            "language": language,
            "enqueue_time": enqueue_time,
            "test": True
        })
        
        self.test_tasks[task_id] = {
            "status": "processing",
            "enqueue_time": enqueue_time,
            "test": True
        }
        
        logger.info("Test task queued", 
                   task_id=task_id,
                   queue_size=self.test_queue.qsize(),
                   engine=engine,
                   language=language)
        
        return task_id

    def test_get_result(self, task_id: str) -> Optional[Dict]:
        """Get result for test task ID"""
        return self.test_tasks.get(task_id)

    async def _test_process_queue(self):
        """Process queued test images"""
        while self.processing:
            try:
                task = await self.test_queue.get()
                task_id = task["task_id"]
                
                # Calculate queue time
                queue_time = time.time() - task["enqueue_time"]
                TEST_QUEUE_TIME.observe(queue_time)
                
                logger.info("Processing test task", 
                           task_id=task_id,
                           queue_time=queue_time)
                
                # Process in thread pool
                start_time = time.time()
                try:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        self.executor,
                        self._test_process_task,
                        task
                    )
                    
                    processing_time = time.time() - start_time
                    TEST_PROCESSING_TIME.observe(processing_time)
                    
                    self.test_tasks[task_id].update({
                        "status": "completed",
                        "result": result,
                        "processing_time": processing_time,
                        "queue_time": queue_time,
                        "test": True
                    })
                    
                    logger.info("Test task completed", 
                              task_id=task_id,
                              processing_time=processing_time)
                    
                except Exception as e:
                    logger.error("Test task failed", 
                               task_id=task_id,
                               error=str(e))
                    self.test_tasks[task_id].update({
                        "status": "failed",
                        "error": str(e),
                        "test": True
                    })
                
                finally:
                    self.test_queue.task_done()
                
            except Exception as e:
                logger.error("Test queue processing error", error=str(e))
                await asyncio.sleep(1)  # Prevent tight loop on persistent errors

    def _test_process_task(self, task: Dict) -> Dict:
        """Process single test OCR task"""
        return self.model_manager.test_process_image(
            task["image_data"],
            engine=task["engine"],
            language=task["language"]
        ) 