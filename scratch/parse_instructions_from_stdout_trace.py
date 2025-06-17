import re
import json

def parse_instructions_from_stdout(file_path):
    """
    Parse instructions from stdout trace of pi0 evaluation.
    Instructions appear at the end of progress bar lines.
    """
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Split into lines
    lines = content.split('\n')
    
    # Dictionary to store results
    results = {}
    current_track = None
    current_task = None
    
    # Regex pattern to match progress lines and extract instructions
    # Pattern: Evaluating {task} of pi0: {percentage}%|{progress_bar}| {current}/{total} [{time_info}]{instruction}
    progress_pattern = r'Evaluating (\w+) of pi0:\s+\d+%\|[^|]*\|\s+\d+/\d+\s+\[[^\]]+\](.+)'
    
    # Pattern to match track information
    track_pattern = r'Running eval for config: .*/(\w+)\.json'
    
    for line in lines:
        # Check if this line indicates a new track
        track_match = re.search(track_pattern, line)
        if track_match:
            current_track = track_match.group(1)
            if current_track not in results:
                results[current_track] = {}
            continue
        
        # Check if this line contains a progress bar with instruction
        progress_match = re.search(progress_pattern, line)
        if progress_match and current_track:
            task = progress_match.group(1)
            instruction = progress_match.group(2).strip()
            
            # Skip empty instructions
            if not instruction:
                continue
                
            # Initialize task list if not exists
            if task not in results[current_track]:
                results[current_track][task] = []
            
            # Add instruction to the task
            results[current_track][task].append(instruction)
    
    return results

def print_results(results):
    """Print the parsed results in a readable format"""
    
    for track, tasks in results.items():
        print(f"\n=== {track.upper().replace('_', ' ')} ===")
        
        for task, instructions in tasks.items():
            print(f"\n{task.upper()}:")
            for i, instruction in enumerate(instructions, 1):
                print(f"  {i:2d}. {instruction}")

def save_results_json(results, output_path):
    """Save results to JSON file"""
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

def main():
    # Parse the stdout file
    input_file = 'scratch/stdout_jun_17_eval'
    output_file = 'scratch/parsed_instructions.json'
    
    print("Parsing instructions from stdout trace...")
    results = parse_instructions_from_stdout(input_file)
    
    # Print results to console
    print_results(results)
    
    # Save to JSON file
    save_results_json(results, output_file)
    print(f"\nResults saved to: {output_file}")
    
    # Print summary statistics
    total_instructions = sum(len(instructions) for track in results.values() 
                           for instructions in track.values())
    print(f"\nSummary:")
    print(f"- Total tracks: {len(results)}")
    print(f"- Total instructions parsed: {total_instructions}")
    
    for track, tasks in results.items():
        track_total = sum(len(instructions) for instructions in tasks.values())
        print(f"- {track}: {track_total} instructions across {len(tasks)} tasks")

if __name__ == "__main__":
    main()
