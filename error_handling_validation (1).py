"""
RoboKen - Enterprise-Grade Error Handling and Validation System

Implements 4-tier error classification with automatic recovery mechanisms
"""

import logging
import traceback
from typing import Optional, Dict, Any, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification"""
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    RESOURCE = "resource"
    TIMEOUT = "timeout"
    PERMISSION = "permission"
    DATA = "data"
    SYSTEM = "system"


@dataclass
class ErrorContext:
    """Context information for error handling"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    timestamp: datetime
    stack_trace: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    metadata: Optional[Dict[str, Any]] = None


class RecoveryStrategy:
    """Base class for recovery strategies"""
    
    async def attempt_recovery(self, context: ErrorContext) -> bool:
        """Attempt to recover from error"""
        raise NotImplementedError


class RetryStrategy(RecoveryStrategy):
    """Retry operation with exponential backoff"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    async def attempt_recovery(self, context: ErrorContext, 
                              operation: Callable) -> bool:
        """Retry operation with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                delay = self.base_delay * (2 ** attempt)
                logger.info(f"Retry attempt {attempt + 1}/{self.max_retries} "
                          f"after {delay}s delay")
                await asyncio.sleep(delay)
                await operation()
                return True
            except Exception as e:
                logger.warning(f"Retry attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    return False
        return False


class FallbackStrategy(RecoveryStrategy):
    """Use fallback mechanism"""
    
    def __init__(self, fallback_operation: Callable):
        self.fallback_operation = fallback_operation
    
    async def attempt_recovery(self, context: ErrorContext) -> bool:
        """Execute fallback operation"""
        try:
            logger.info("Attempting fallback strategy")
            await self.fallback_operation()
            return True
        except Exception as e:
            logger.error(f"Fallback strategy failed: {e}")
            return False


class ErrorHandler:
    """Main error handling system"""
    
    def __init__(self):
        self.error_log: list[ErrorContext] = []
        self.recovery_strategies: Dict[ErrorCategory, RecoveryStrategy] = {}
        self.error_count = 0
    
    def register_recovery_strategy(self, category: ErrorCategory, 
                                   strategy: RecoveryStrategy):
        """Register a recovery strategy for an error category"""
        self.recovery_strategies[category] = strategy
        logger.info(f"Registered recovery strategy for {category.value}")
    
    def classify_error(self, exception: Exception) -> tuple[ErrorCategory, ErrorSeverity]:
        """Classify error by type and determine severity"""
        error_type = type(exception).__name__
        error_message = str(exception).lower()
        
        # Network errors
        if any(keyword in error_message for keyword in 
               ['connection', 'network', 'timeout', 'unreachable']):
            return ErrorCategory.NETWORK, ErrorSeverity.MEDIUM
        
        # Authentication errors
        if any(keyword in error_message for keyword in 
               ['auth', 'permission', 'unauthorized', 'forbidden']):
            return ErrorCategory.AUTHENTICATION, ErrorSeverity.HIGH
        
        # Validation errors
        if any(keyword in error_message for keyword in 
               ['invalid', 'validation', 'format', 'parse']):
            return ErrorCategory.VALIDATION, ErrorSeverity.LOW
        
        # Resource errors
        if any(keyword in error_message for keyword in 
               ['memory', 'disk', 'resource', 'limit']):
            return ErrorCategory.RESOURCE, ErrorSeverity.HIGH
        
        # Timeout errors
        if 'timeout' in error_message:
            return ErrorCategory.TIMEOUT, ErrorSeverity.MEDIUM
        
        # Default to system error
        return ErrorCategory.SYSTEM, ErrorSeverity.CRITICAL
    
    async def handle_error(self, exception: Exception, 
                          operation: Optional[Callable] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> ErrorContext:
        """Handle an error with automatic recovery attempt"""
        self.error_count += 1
        
        # Classify error
        category, severity = self.classify_error(exception)
        
        # Create error context
        context = ErrorContext(
            error_id=f"err_{self.error_count}_{int(datetime.now().timestamp())}",
            category=category,
            severity=severity,
            message=str(exception),
            timestamp=datetime.now(),
            stack_trace=traceback.format_exc(),
            metadata=metadata or {}
        )
        
        logger.error(f"Error {context.error_id}: {category.value} - {severity.value}")
        logger.error(f"Message: {context.message}")
        
        # Attempt recovery if strategy exists and operation provided
        if category in self.recovery_strategies and operation:
            context.recovery_attempted = True
            strategy = self.recovery_strategies[category]
            
            try:
                if isinstance(strategy, RetryStrategy):
                    success = await strategy.attempt_recovery(context, operation)
                else:
                    success = await strategy.attempt_recovery(context)
                
                context.recovery_successful = success
                
                if success:
                    logger.info(f"Recovery successful for error {context.error_id}")
                else:
                    logger.warning(f"Recovery failed for error {context.error_id}")
            
            except Exception as recovery_error:
                logger.error(f"Recovery attempt raised exception: {recovery_error}")
                context.recovery_successful = False
        
        # Log error
        self.error_log.append(context)
        
        # Alert on critical errors
        if severity == ErrorSeverity.CRITICAL:
            await self._send_critical_alert(context)
        
        return context
    
    async def _send_critical_alert(self, context: ErrorContext):
        """Send alert for critical errors"""
        logger.critical(f"CRITICAL ERROR ALERT: {context.error_id}")
        logger.critical(f"Category: {context.category.value}")
        logger.critical(f"Message: {context.message}")
        # In production, this would send email/SMS/Slack notification
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        if not self.error_log:
            return {
                'total_errors': 0,
                'by_category': {},
                'by_severity': {},
                'recovery_rate': 0.0
            }
        
        by_category = {}
        by_severity = {}
        recovery_attempts = 0
        recovery_successes = 0
        
        for error in self.error_log:
            # Count by category
            cat = error.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
            
            # Count by severity
            sev = error.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
            
            # Track recovery
            if error.recovery_attempted:
                recovery_attempts += 1
                if error.recovery_successful:
                    recovery_successes += 1
        
        recovery_rate = (
            recovery_successes / recovery_attempts 
            if recovery_attempts > 0 else 0.0
        )
        
        return {
            'total_errors': len(self.error_log),
            'by_category': by_category,
            'by_severity': by_severity,
            'recovery_attempts': recovery_attempts,
            'recovery_successes': recovery_successes,
            'recovery_rate': recovery_rate
        }


class InputValidator:
    """Validate user inputs and parameters"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        import re
        pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_command(command: str) -> tuple[bool, Optional[str]]:
        """Validate automation command"""
        if not command or len(command.strip()) == 0:
            return False, "Command cannot be empty"
        
        if len(command) > 1000:
            return False, "Command too long (max 1000 characters)"
        
        # Check for potentially dangerous commands
        dangerous_keywords = ['rm -rf', 'format', 'delete system']
        for keyword in dangerous_keywords:
            if keyword in command.lower():
                return False, f"Command contains dangerous keyword: {keyword}"
        
        return True, None
    
    @staticmethod
    def validate_task_parameters(params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate task parameters"""
        if not isinstance(params, dict):
            return False, "Parameters must be a dictionary"
        
        # Check for required fields based on task type
        if 'type' in params:
            task_type = params['type']
            
            if task_type == 'web_automation' and 'url' in params:
                if not InputValidator.validate_url(params['url']):
                    return False, "Invalid URL format"
            
            if task_type == 'email' and 'to' in params:
                if not InputValidator.validate_email(params['to']):
                    return False, "Invalid email format"
        
        return True, None


# Example usage
async def demo_error_handling():
    """Demonstrate error handling system"""
    handler = ErrorHandler()
    
    # Register recovery strategies
    handler.register_recovery_strategy(
        ErrorCategory.NETWORK,
        RetryStrategy(max_retries=3, base_delay=1.0)
    )
    
    # Simulate various errors
    errors_to_test = [
        ConnectionError("Network connection failed"),
        ValueError("Invalid input format"),
        PermissionError("Unauthorized access attempt"),
        TimeoutError("Operation timed out"),
    ]
    
    for error in errors_to_test:
        context = await handler.handle_error(error)
        print(f"\nHandled: {context.error_id}")
        print(f"Category: {context.category.value}")
        print(f"Severity: {context.severity.value}")
    
    # Print statistics
    stats = handler.get_error_statistics()
    print("\n" + "="*60)
    print("ERROR HANDLING STATISTICS")
    print("="*60)
    print(f"Total Errors: {stats['total_errors']}")
    print(f"By Category: {stats['by_category']}")
    print(f"By Severity: {stats['by_severity']}")
    print(f"Recovery Rate: {stats['recovery_rate']*100:.1f}%")


if __name__ == "__main__":
    asyncio.run(demo_error_handling())
