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
        import sys
        
        # Skip in migrations, makemigrations, collectstatic, etc
        skip_commands = ['migrate', 'makemigrations', 'collectstatic', 'createsuperuser', 'shell']
        if any(cmd in sys.argv for cmd in skip_commands):
            return
        
        # Only run once when Django is fully ready (skip reloader process)
        # runserver with auto-reload creates 2 processes, we only want the main one
        if os.environ.get('RUN_MAIN') != 'true' and 'runserver' in sys.argv:
            return
            
        try:
            import time
            from project.models import ModbusConfig
            from project.modbus_service import ModbusService
            
            # Small delay to ensure database is ready
            time.sleep(1)
            
            # Check if auto-start is enabled
            try:
                config = ModbusConfig.objects.first()
                if config and config.auto_start:
                    logger.info("🔄 Auto-starting Modbus service...")
                    service = ModbusService()
                    
                    # Check if already running
                    if service.is_running():
                        logger.info("ℹ️ Modbus already running, skipping auto-start")
                        return
                    
                    host = config.android_ip or '0.0.0.0'
                    port = config.android_port or 9502
                    
                    result = service.start(host, port)
                    if result['success']:
                        logger.info(f"✅ Modbus auto-started on {host}:{port}")
                        print(f"✅ Modbus auto-started on {host}:{port}")
                    else:
                        logger.warning(f"⚠️ Modbus auto-start failed: {result['message']}")
                        print(f"⚠️ Modbus auto-start failed: {result['message']}")
                else:
                    logger.info("ℹ️ Modbus auto-start disabled in config")
                    
            except ModbusConfig.DoesNotExist:
                logger.info("ℹ️ No Modbus config found, skipping auto-start")
            except Exception as e:
                logger.error(f"❌ Error checking Modbus config: {e}")
                
        except Exception as e:
            logger.error(f"❌ Error in Modbus auto-start: {e}")
