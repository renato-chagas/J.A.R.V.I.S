from jarvis.interfaces.cli.commands.base_command import BaseCommand

class SystemHealthCommand(BaseCommand):
    """Command to check and display real-time hardware status."""

    def __init__(self, system_health):
        self.system_health = system_health

    def matches(self, text: str) -> bool:
        text_clean = text.lower().strip()
        
        return (
            "status" in text_clean or 
            "saude" in text_clean or 
            "saúde" in text_clean or 
            "diagnostico" in text_clean or 
            "diagnóstico" in text_clean
        )

    def execute(self, text: str, context: dict) -> str:
        try:

            health = self.system_health.get_system_health()
            
            # Format report beautifully to return to the interface router
            report = (
                "\n======= SYSTEM HARDWARE STATUS =======\n"
                f"💻 CPU Usage: {health['cpu_percent']}%\n"
                f"🧠 RAM Memory: {health['ram_used_gb']}GB / {health['ram_total_gb']}GB ({health['ram_percent']}%)\n"
                f"💽 Disk Storage: {health['disk_used_gb']}GB / {health['disk_total_gb']}GB ({health['disk_percent']}%)\n"
                "======================================="
            )
            return report
        except Exception as e:
            return f"Sir, I encountered an error checking system signals: {e}"