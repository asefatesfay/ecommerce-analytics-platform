#!/bin/bash

# Mermaid Diagram Export Script
# Generates PNG/SVG images from Mermaid text files

set -e

echo "🎨 Mermaid Diagram Export Script"
echo "=================================="

# Check if mermaid-cli is installed
if ! command -v mmdc &> /dev/null; then
    echo "❌ mermaid-cli not found. Installing..."
    npm install -g @mermaid-js/mermaid-cli
fi

# Create output directory
MERMAID_DIR="docs/architecture/mermaid"
OUTPUT_DIR="$MERMAID_DIR/generated-images"
mkdir -p "$OUTPUT_DIR"

echo "📁 Processing Mermaid files from: $MERMAID_DIR"
echo "💾 Saving images to: $OUTPUT_DIR"

# Process each .mmd file
for mmd_file in "$MERMAID_DIR"/*.mmd; do
    if [ -f "$mmd_file" ]; then
        filename=$(basename "$mmd_file" .mmd)
        
        echo "🔄 Processing: $filename"
        
        # Generate PNG (high resolution)
        mmdc -i "$mmd_file" -o "$OUTPUT_DIR/${filename}.png" \
             --width 1200 --height 800 --scale 2 \
             --backgroundColor white --theme default
        
        # Generate SVG (vector format)
        mmdc -i "$mmd_file" -o "$OUTPUT_DIR/${filename}.svg" \
             --backgroundColor white --theme default
        
        echo "✅ Generated: ${filename}.png and ${filename}.svg"
    fi
done

echo ""
echo "🎉 Export complete! Generated images:"
ls -la "$OUTPUT_DIR"

echo ""
echo "📖 Usage:"
echo "  - Use .mmd files for GitHub rendering"
echo "  - Use .png files for presentations"
echo "  - Use .svg files for scalable graphics"