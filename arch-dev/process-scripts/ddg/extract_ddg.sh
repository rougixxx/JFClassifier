#!/bin/bash
# filepath: /home/pain/Desktop/r3i-stuff/pfe/static-code-analysis/jvFinder/process-scripts/ddg/extract_ddg.sh

# Configuration 
JAVA_FILES_FOLDER="$HOME/Desktop/r3i-stuff/pfe/static-code-analysis/jvFinder/dataset/java-files"
OUTPUT_DIR="$HOME/Desktop/r3i-stuff/pfe/static-code-analysis/jvFinder/dataset/ddg/ddg-dot-files"  # Changed to DDG
JOERN_CLI_PATH="$HOME/Desktop/r3i-stuff/pfe/static-code-analysis/jvFinder/joern/joern-cli/joern"
TEMP_DIR="$OUTPUT_DIR/temp"
NUM_PARALLEL=7  # Number of parallel jobs to run
workspace_dir="./workspace"
failed_imports="$OUTPUT_DIR/failed_imports.txt"
# Fixed batch size
FILES_PER_BATCH=6000  # Fixed at 6000 files per batch

# Ensure directories exist
mkdir -p "$OUTPUT_DIR"
mkdir -p "$TEMP_DIR"

# Create file list
echo "Creating file list..."
#find "$JAVA_FILES_FOLDER" -name "*.java" > "$TEMP_DIR/all_files.txt"
total_files=$(wc -l < "$TEMP_DIR/all_files.txt")

echo "Found $total_files Java files to process"
echo "Using fixed batch size of $FILES_PER_BATCH files per batch"

# Split the file list with fixed size
rm -rf "$TEMP_DIR/batch_"* 2>/dev/null
split -l $FILES_PER_BATCH "$TEMP_DIR/all_files.txt" "$TEMP_DIR/batch_"

# Calculate number of batches
num_batches=$(find "$TEMP_DIR" -name "batch_*" | wc -l)
echo "Created $num_batches batches"

# Function to clear the workspace
clean_workspace() {
    while true; do
        if [ -d "$workspace_dir" ]; then
            echo "Cleaning workspace directory..."
            rm -rf "$workspace_dir"/* 2>/dev/null
        fi
        sleep 3600
    done
}

# Function to process a single batch
process_batch() {
    local batch_file=$1
    local batch_num=$(basename "$batch_file" | sed 's/batch_//')
    local batch_dir="$TEMP_DIR/batch_"$batch_num"_dir"

    # Create batch directory
    mkdir -p "$batch_dir"
    
    echo "Starting batch $batch_num ($(wc -l < "$batch_file") files)"

    # Run Joern for this batch with allocated memory
    # Note: Changed to generate_dot_ddg.sc for DDG generation
    "$JOERN_CLI_PATH" --script "./generate_dot_ddg.sc" \
        --param fileListPath="$batch_file" \
        --param outputDir="$OUTPUT_DIR" \
         2> "$batch_dir/errors.log"
    
    local exit_status=$?
    if [ $exit_status -ne 0 ]; then
        echo "[$batch_num] Errors occurred during DDG generation"
        echo "[$batch_num] See $batch_dir/errors.log for details"
        
        # Add to failed files
        echo "Batch $batch_num" >> "$OUTPUT_DIR/temp/failed_batches.txt"
    fi
    
    echo "[$batch_num] Batch processing complete"
    
    # Count results for this batch
    local batch_dots=$(find "$OUTPUT_DIR" -newer "$batch_file" -name "*.dot" | wc -l)
    echo "[$batch_num] Generated $batch_dots DOT files"
}

# Initialize results file
> "$OUTPUT_DIR/failed_batches.txt"
start_time=$(date +%s)

echo "Starting parallel processing with $NUM_PARALLEL jobs at $(date)"

# Run batches in parallel
batch_files=$(find "$TEMP_DIR" -name "batch_*" | sort)
pids=()
clean_workspace &  # Start workspace cleaner in background
cleaner_pid=$!

for batch_file in $batch_files; do
    # Check if we've reached max parallel processes
    while [ ${#pids[@]} -ge $NUM_PARALLEL ]; do
        # Wait for any process to finish
        for i in "${!pids[@]}"; do
            if ! kill -0 ${pids[$i]} 2>/dev/null; then
                unset pids[$i]
            fi
        done
        pids=("${pids[@]}") # Reindex array
        sleep 1
    done
    
    # Start a new batch process
    process_batch "$batch_file" &

    pids+=($!)
    
    # Small delay to avoid race conditions
    sleep 2
done

# Wait for all remaining processes to complete
for pid in "${pids[@]}"; do
    wait $pid
done
kill $cleaner_pid 2>/dev/null
end_time=$(date +%s)
duration=$((end_time - start_time))

# Count overall results
total_dots=$(find "$OUTPUT_DIR" -name "*.dot" | wc -l)
failed_batches=$(wc -l < "$OUTPUT_DIR/failed_batches.txt" 2>/dev/null || echo 0)
failed_imports_count=$(wc -l $failed_imports  | cut -d ' ' -f 1)
# Print summary
echo ""
echo "==== Processing Summary ===="
echo "Finished parallel processing at $(date)"
echo "Total Java files: $total_files"
echo "Total DOT files generated: $total_dots"
echo "Success rate: $(( (total_dots * 100) / total_files ))%"
echo "Failed batches: $failed_batches"
echo ""
echo "Number of failed imports is: $failed_imports_count"

echo "Total processing time: $(( duration / 60 )) minutes $(( duration % 60 )) seconds"

# Clean up temp files if all successful
if [ "$failed_batches" -eq 0 ]; then
    echo "All batches completed successfully, cleaning up temporary files"
    rm -rf "$TEMP_DIR"
else
    echo "Some batches failed, keeping temporary files for inspection"
    echo "See $OUTPUT_DIR/failed_batches.txt for list of failed batches"
fi