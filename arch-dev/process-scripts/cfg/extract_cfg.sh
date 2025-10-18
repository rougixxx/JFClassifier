#!/bin/bash
# filepath: /home/pain/Desktop/r3i-stuff/pfe/static-code-analysis/jvFinder/process-scripts/cfg/parallel_extract_cfg.sh

# Configuration 
JAVA_FILES_FOLDER="/home/pain/Desktop/r3i-stuff/pfe/static-code-analysis/jvFinder/dataset/java-files"
OUTPUT_DIR="$HOME/Desktop/r3i-stuff/pfe/static-code-analysis/jvFinder/dataset/cfg-dot-files"
JOERN_CLI_PATH="/home/pain/Desktop/r3i-stuff/pfe/static-code-analysis/jvFinder/joern/joern-cli/joern"
TEMP_DIR="$OUTPUT_DIR/temp"
NUM_PARALLEL=7  # Number of parallel jobs to run
workspace_dir="./workspace"
# Ensure directories exist
mkdir -p "$OUTPUT_DIR"
mkdir -p "$TEMP_DIR"

# Create file list
echo "Creating file list..."
find "$JAVA_FILES_FOLDER" -name "*.java" > "$TEMP_DIR/all_files.txt"
total_files=$(wc -l < "$TEMP_DIR/all_files.txt")
# Calculate optimal batch size based on number of cores and files
# Target around 10-15 batches for better load distribution
TARGET_BATCHES=$((NUM_PARALLEL * 2))  # 2 batches per parallel job is a good balance
FILES_PER_BATCH=$((total_files / TARGET_BATCHES))

# Make sure batch size is reasonable (between 2000-10000 files)
if [ $FILES_PER_BATCH -lt 2000 ]; then
    FILES_PER_BATCH=2000
elif [ $FILES_PER_BATCH -gt 10000 ]; then
    FILES_PER_BATCH=10000
fi

echo "Optimal batch size: $FILES_PER_BATCH files per batch"
echo "Splitting into batches..."
echo "Found $total_files Java files to process"
echo "Splitting into batches of $FILES_PER_BATCH files each"

# Split the file list with fixed size
rm -f "$TEMP_DIR/batch_"* 2>/dev/null
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
            sleep 60
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

 # ./joern --script ../../process-scripts/cfg/generate_dot_cfg.sc --param fileListPath=../../dataset/cfg-dot-files/temp/batch_aa --param outputDir=../../dataset/cfg-dot-files
    # Run Joern for this batch with allocated memory
 "$JOERN_CLI_PATH" --script "./generate_dot_cfg.sc" --param fileListPath="$batch_file" --param outputDir="$OUTPUT_DIR" 2> "$batch_dir/errors.log"
    
    local exit_status=$?
    if [ $exit_status -ne 0 ]; then
        echo "[$batch_num] Errors occurred during CFG generation"
        echo "[$batch_num] See $batch_dir/errors.log for details"
        
        # Add to failed files
        echo "Batch $batch_num" >> "$OUTPUT_DIR/failed_batches.txt"
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
    # batch_aa batch_ab etc
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

# Print summary
echo ""
echo "==== Processing Summary ===="
echo "Finished parallel processing at $(date)"
echo "Total Java files: $total_files"
echo "Total DOT files generated: $total_dots"
echo "Success rate: $(( (total_dots * 100) / total_files ))%"
echo "Failed batches: $failed_batches"
echo "Total processing time: $(( duration / 60 )) minutes $(( duration % 60 )) seconds"

# Clean up temp files if all successful
if [ "$failed_batches" -eq 0 ]; then
    echo "All batches completed successfully, cleaning up temporary files"
    rm -rf "$TEMP_DIR"
else
    echo "Some batches failed, keeping temporary files for inspection"
    echo "See $OUTPUT_DIR/failed_batches.txt for list of failed batches"
fi