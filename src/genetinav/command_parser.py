def parse_command(input_str: str, valid_commands: list[str] | None = None) -> tuple[str | None, str, str | None]:
    """Parse a slash command or return as a raw query.
    
    Returns:
        (command_name, arguments, error_message)
    """
    s = input_str.strip()
    if not s:
        return None, "", None
        
    if s.startswith("/"):
        parts = s[1:].split(" ", 1)
        raw_cmd = parts[0].strip().lower()
        args = parts[1].strip() if len(parts) > 1 else ""
        
        if valid_commands is not None and raw_cmd:
            if raw_cmd in valid_commands:
                return raw_cmd, args, None
                
            prefix_matches = [cmd for cmd in valid_commands if cmd.startswith(raw_cmd)]
            
            if len(prefix_matches) == 1:
                return prefix_matches[0], args, None
            elif len(prefix_matches) > 1:
                pick_list = " ".join(f"{i+1}) /{cmd}" for i, cmd in enumerate(prefix_matches))
                return None, "", f"Ambiguous command. Did you mean: {pick_list}"
            else:
                return None, "", f"Unknown command: /{raw_cmd}"
                
        return raw_cmd, args, None
        
    return None, s, None
