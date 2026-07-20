import os
import shutil
import logging

backend_version = "0.0.1"

class CommandProcessor:
    def execute(self, cmd_str):
        parts = cmd_str.split()
        if not parts: return "Empty command"

        action = parts[0].lower()
        try:
            if action == "delete":
                if len(parts) < 2:
                    return "Error: Missing filename for delete"

                filename = parts[1]
                path = os.path.join("storage", filename)

                if os.path.exists(filename):
                    os.remove(filename)
                    logging.info(f"Deleted file: {filename}")
                    return f"Deleted {filename}"
                return f"Error: File {filename} not found in storage"

            elif action == "move":
                if len(parts) < 3:
                    return "Error: Missing source or destination for move"
                src, dest = parts[1], parts[2]
                src_path = os.path.join("storage", src)
                dest_path = os.path.join("storage", dest)

                if not os.path.exists(src_path):
                    return f"Error: Source path {src} not found in storage"

                shutil.move(src, dest)
                logging.info(f"Moved: {src} to {dest}")
                return f"Moved {src} to {dest}"

            elif action == "version":
                version = backend_version
                return f"Current FileLauncher Backend Version: {version}"

            return "Unknown command"
        except Exception as e:
            return f"Error executing command: {str(e)}"