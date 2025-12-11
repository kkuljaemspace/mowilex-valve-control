"""
Django AppConfig untuk auto-start Modbus service
"""
import logging
import os
from django.apps import AppConfig

logger = logging.getLogger(__name__)


class ProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'project'
    
    def ready(self):
        """
        Called when Django starts
        Auto-start Modbus service if configured
        """
        # Avoid running in manage.py migrations/collectstatic
        import sys
        if 'runserver' not in sys.argv and 'main.py' not in str(sys.argv):
            return
        
        # Only run in main process (not reloader)
        if os.environ.get('RUN_MAIN') == 'true':
            return
            
        try:
            from project.models import ModbusConfig
            from project.modbus_service import ModbusService
            import time
            
            # Wait a bit for Django to fully initialize
            time.sleep(2)
            
            # Check if auto-start is enabled
            try:
                config = ModbusConfig.objects.first()
                if config and config.auto_start:
                    logger.info("🔄 Auto-starting Modbus service...")
                    service = ModbusService()
                    
                    host = config.android_ip or '0.0.0.0'
                    port = config.android_port or 9502
                    
                    result = service.start(host, port)
                    if result['success']:
                        logger.info(f"✅ Modbus auto-started: {result['message']}")
                    else:
                        logger.warning(f"⚠️ Modbus auto-start failed: {result['message']}")
                else:
                    logger.info("ℹ️ Modbus auto-start disabled in config")
            except Exception as e:
                logger.error(f"❌ Error checking Modbus config: {e}")
                
        except Exception as e:
            logger.error(f"❌ Error in Modbus auto-start: {e}")
