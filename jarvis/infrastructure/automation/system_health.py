import psutil
import logging

class SystemHealth:
    """Responsible for reading hardware telemetry and system health."""
    
    def get_system_health(self) -> dict:
        """Retrieves real-time CPU, RAM, and Disk metrics."""
        try:
            cpu_usage = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                "cpu_percent": cpu_usage,
                "ram_total_gb": round(ram.total / (1024**3), 2),
                "ram_used_gb": round(ram.used / (1024**3), 2),
                "ram_percent": ram.percent,
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_percent": disk.percent
            }
        except Exception as e:
            logging.error(f"Failed to fetch system metrics: {e}")
            raise RuntimeError(f"Could not read system signals: {e}")