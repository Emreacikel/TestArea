import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import re
from pathlib import Path
import fitz  # PyMuPDF
from tkinter import ttk

class BookSummaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Summary")
        
        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Set window size to screen size
        self.root.geometry(f"{screen_width}x{screen_height}")
        
        # Calculate widths for each section
        params_width = int(screen_width * 0.25)  # 1/4 of screen width
        contents_width = int(screen_width * 0.25)  # 1/4 of screen width
        main_width = int(screen_width * 0.5)  # 1/2 of screen width
        
        # Configure main window grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0)  # No weight to respect fixed width
        self.root.grid_columnconfigure(1, weight=0)  # No weight to respect fixed width
        self.root.grid_columnconfigure(2, weight=0)  # No weight to respect fixed width
        
        # Left frame for parameters (1/4 width)
        parameters_frame = ttk.Frame(root, padding="10", width=params_width)
        parameters_frame.grid(row=0, column=0, sticky="nsew")
        parameters_frame.grid_propagate(False)  # Prevent frame from shrinking
        parameters_frame.grid_columnconfigure(0, weight=1)
        
        # Add all parameter controls to parameters_frame
        self.setup_parameter_controls(parameters_frame)
        
        # Middle frame for contents (1/4 width)
        contents_frame = ttk.Frame(root, padding="10", width=contents_width)
        contents_frame.grid(row=0, column=1, sticky="nsew")
        contents_frame.grid_propagate(False)  # Prevent frame from shrinking
        contents_frame.grid_columnconfigure(0, weight=1)
        contents_frame.grid_rowconfigure(1, weight=1)
        
        # Label for Contents
        ttk.Label(contents_frame, text="Contents").grid(row=0, column=0, sticky="w")
        
        # Contents text area
        self.contents_area = tk.Text(contents_frame, wrap=tk.WORD, font=('Arial', 12))
        contents_scrollbar = ttk.Scrollbar(contents_frame, orient=tk.VERTICAL, command=self.contents_area.yview)
        self.contents_area.configure(yscrollcommand=contents_scrollbar.set)
        
        self.contents_area.grid(row=1, column=0, sticky="nsew")
        contents_scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Right frame for main text (1/2 width)
        main_text_frame = ttk.Frame(root, padding="10", width=main_width)
        main_text_frame.grid(row=0, column=2, sticky="nsew")
        main_text_frame.grid_propagate(False)  # Prevent frame from shrinking
        main_text_frame.grid_columnconfigure(0, weight=1)
        main_text_frame.grid_rowconfigure(1, weight=1)
        
        # Label for Main Text
        ttk.Label(main_text_frame, text="Main Text").grid(row=0, column=0, sticky="w")
        
        # Main text area
        self.text_area = tk.Text(main_text_frame, wrap=tk.WORD, font=('Arial', 12))
        text_scrollbar = ttk.Scrollbar(main_text_frame, orient=tk.VERTICAL, command=self.text_area.yview)
        self.text_area.configure(yscrollcommand=text_scrollbar.set)
        
        self.text_area.grid(row=1, column=0, sticky="nsew")
        text_scrollbar.grid(row=1, column=1, sticky="ns")
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=1, column=0, columnspan=3, sticky="ew")
        
    def setup_parameter_controls(self, parent):
        """Setup all parameter controls in the left frame"""
        # Title with smaller font
        tk.Label(
            parent,
            text="Book Summary",
            font=('Arial', 16, 'bold'),  # Reduced from 24 to 16
            bg='#f0f0f0'
        ).grid(row=0, column=0, sticky="ew", pady=(10, 15))  # Reduced padding
        
        # Page range frame with reduced padding
        page_frame = tk.LabelFrame(parent, text="Page Range", bg='#f0f0f0', padx=5, pady=5)  # Reduced padding
        page_frame.grid(row=1, column=0, sticky="ew", padx=5)  # Reduced padding
        
        # Create a single row for page range inputs
        page_row = tk.Frame(page_frame, bg='#f0f0f0')
        page_row.grid(row=0, column=0, sticky="ew")
        
        # Start page on the left
        start_container = tk.Frame(page_row, bg='#f0f0f0')
        start_container.grid(row=0, column=0, padx=(0, 5))  # Reduced padding
        
        tk.Label(start_container, text="Start:", bg='#f0f0f0', font=('Arial', 10)).grid(row=0, column=0)  # Reduced text and font
        self.start_page = tk.Entry(start_container, width=5)  # Reduced width
        self.start_page.grid(row=0, column=1, padx=2)  # Reduced padding
        
        # End page on the right
        end_container = tk.Frame(page_row, bg='#f0f0f0')
        end_container.grid(row=0, column=1)
        
        tk.Label(end_container, text="End:", bg='#f0f0f0', font=('Arial', 10)).grid(row=0, column=0)  # Reduced text and font
        self.end_page = tk.Entry(end_container, width=5)  # Reduced width
        self.end_page.grid(row=0, column=1, padx=2)  # Reduced padding
        
        # Add minimal spacing between frames
        tk.Frame(parent, height=10, bg='#f0f0f0').grid(row=2, column=0)  # Reduced spacing
        
        # Contents page range frame
        contents_pages_frame = tk.LabelFrame(parent, text="Contents Pages", bg='#f0f0f0', padx=5, pady=5)  # Reduced padding
        contents_pages_frame.grid(row=3, column=0, sticky="ew", padx=5)  # Reduced padding

        # Create left and right frames within contents_pages_frame
        contents_left_frame = ttk.Frame(contents_pages_frame)
        contents_left_frame.grid(row=0, column=0, sticky='w')
        contents_right_frame = ttk.Frame(contents_pages_frame)
        contents_right_frame.grid(row=0, column=1, sticky='e')

        # Left side - Start
        tk.Label(contents_left_frame, text="Start:", bg='#f0f0f0', font=('Arial', 10)).grid(row=0, column=0)
        self.start_page_entry = tk.Entry(contents_left_frame, width=5)
        self.start_page_entry.grid(row=0, column=1, padx=2)

        # Right side - End
        tk.Label(contents_right_frame, text="End:", bg='#f0f0f0', font=('Arial', 10)).grid(row=0, column=0, sticky='e')
        self.end_page_entry = tk.Entry(contents_right_frame, width=5)
        self.end_page_entry.grid(row=0, column=1, padx=2)

        # Add minimal spacing
        tk.Frame(parent, height=10, bg='#f0f0f0').grid(row=4, column=0)  # Reduced spacing

        # Endnotes parameter frame
        endnotes_frame = tk.LabelFrame(parent, text="Endnotes", bg='#f0f0f0', padx=5, pady=5)
        endnotes_frame.grid(row=5, column=0, sticky="ew", padx=5)
        
        # Initialize special_chars as a StringVar with only special symbols
        self.special_chars = tk.StringVar(value="* † ‡ § # ¶ ∥")  # Special symbols with spaces
        
        # Special characters input in a more compact layout
        chars_container = tk.Frame(endnotes_frame, bg='#f0f0f0')
        chars_container.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        tk.Label(
            chars_container,
            text="Starting Chars:",
            bg='#f0f0f0',
            font=('Arial', 10)
        ).grid(row=0, column=0, padx=2)
        
        # Width adjusted for spaced special characters
        self.start_chars_entry = tk.Entry(chars_container, width=15, textvariable=self.special_chars)
        self.start_chars_entry.grid(row=0, column=1, padx=2)
        
        # Button container for endnote operations - moved to row 1
        endnote_buttons = tk.Frame(endnotes_frame, bg='#f0f0f0')
        endnote_buttons.grid(row=1, column=0, columnspan=2, sticky="ew", padx=2)  # Changed to row=1
        
        # Mark Endnotes button
        self.mark_endnotes_button = tk.Button(
            endnote_buttons,
            text="Mark Endnotes",
            command=self.mark_endnotes,
            font=('Arial', 11),
            padx=10,
            pady=5
        )
        self.mark_endnotes_button.grid(row=0, column=0, padx=5)
        
        # Remove Endnotes button
        self.remove_endnotes_button = tk.Button(
            endnote_buttons,
            text="Remove Endnotes",
            command=self.remove_endnotes,
            font=('Arial', 11),
            padx=10,
            pady=5
        )
        self.remove_endnotes_button.grid(row=0, column=1, padx=5)
        
        # Configure grid weights
        parent.grid_columnconfigure(0, weight=1)
        page_frame.grid_columnconfigure(0, weight=1)
        page_row.grid_columnconfigure(1, weight=1)
        contents_pages_frame.grid_columnconfigure(3, weight=1)
        endnotes_frame.grid_columnconfigure(0, weight=1)
        chars_container.grid_columnconfigure(1, weight=1)
        
        # Headers parameter frame
        headers_frame = tk.LabelFrame(parent, text="Headers", bg='#f0f0f0', padx=10, pady=10)
        headers_frame.grid(row=7, column=0, sticky="ew", padx=20)
        
        # Max Header length input
        max_header_container = tk.Frame(headers_frame, bg='#f0f0f0')
        max_header_container.grid(row=0, column=0, sticky="ew")
        
        tk.Label(
            max_header_container,
            text="Max Header Length:",
            bg='#f0f0f0'
        ).grid(row=0, column=0)
        
        self.max_header_length_entry = tk.Entry(max_header_container, width=5)
        self.max_header_length_entry.insert(0, "50")  # Default value
        self.max_header_length_entry.grid(row=0, column=1, padx=5)
        
        # Button container for Mark and Remove Headers
        button_container = tk.Frame(headers_frame, bg='#f0f0f0')
        button_container.grid(row=1, column=0, pady=5)

        # Mark Headers button
        self.mark_headers_button = tk.Button(
            button_container,
            text="Mark Headers",
            command=self.mark_headers,
            font=('Arial', 11),
            padx=10,
            pady=5
        )
        self.mark_headers_button.grid(row=0, column=0, padx=5)

        # Remove Headers button
        self.remove_headers_button = tk.Button(
            button_container,
            text="Remove Headers",
            command=self.remove_headers,
            font=('Arial', 11),
            padx=10,
            pady=5
        )
        self.remove_headers_button.grid(row=0, column=1, padx=5)
        
        # New parameter group for Mark Page N
        page_number_frame = tk.LabelFrame(parent, text="Page Numbers", bg='#f0f0f0', padx=10, pady=10)
        page_number_frame.grid(row=8, column=0, sticky="ew", padx=20, pady=(10, 0))

        # Mark Page N button
        self.mark_page_n_button = tk.Button(
            page_number_frame,
            text="Mark Page N",
            command=self.mark_page_numbers,
            font=('Arial', 11),
            padx=10,
            pady=5
        )
        self.mark_page_n_button.grid(row=0, column=0, padx=5)

        # Remove Page N button
        self.remove_page_n_button = tk.Button(
            page_number_frame,
            text="Remove Page N",
            command=self.remove_page_numbers,
            font=('Arial', 11),
            padx=10,
            pady=5
        )
        self.remove_page_n_button.grid(row=0, column=1, padx=5)
        
        # Create a frame for the buttons at the bottom of left panel
        button_frame = tk.Frame(parent, bg='#f0f0f0')
        button_frame.grid(row=9, column=0, sticky="ew", pady=20)
        
        # Button container
        button_container = tk.Frame(button_frame, bg='#f0f0f0')
        button_container.grid(row=0, column=0, sticky="ew")
        
        # Configure button container for centering
        button_container.grid_columnconfigure(0, weight=1)
        button_container.grid_columnconfigure(2, weight=1)
        
        # Upload button
        self.upload_button = tk.Button(
            button_container,
            text="Upload PDF",
            command=self.upload_pdf,
            font=('Arial', 12),
            padx=20,
            pady=10
        )
        self.upload_button.grid(row=0, column=0, padx=10)
        
        # Refine button (initially disabled)
        self.refine_button = tk.Button(
            button_container,
            text="Refine",
            command=self.refine_pdf,
            font=('Arial', 12),
            padx=20,
            pady=10,
            state='disabled'
        )
        self.refine_button.grid(row=0, column=1, padx=10)

    def validate_page_range(self, total_pages):
        try:
            start = int(self.start_page.get() or '1')
            end = int(self.end_page.get() or str(total_pages))
            
            # Adjust for 1-based index
            start = max(1, min(start, total_pages))
            end = max(1, min(end, total_pages))
            
            if start >= end:
                messagebox.showerror("Error", "Start page must be less than end page")
                return None, None
                
            return start, end
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid page numbers")
            return None, None

    def validate_contents_range(self, total_pages):
        # If both fields are empty, return None
        if not self.start_page_entry.get() and not self.end_page_entry.get():
            return None, None
            
        # If only one field is filled, show error
        if bool(self.start_page_entry.get()) != bool(self.end_page_entry.get()):
            messagebox.showerror("Error", "Please fill both contents page fields or leave both empty")
            return None, None
            
        try:
            start = int(self.start_page_entry.get())
            end = int(self.end_page_entry.get())
            
            # Adjust for 1-based index and validate range
            if start < 1 or end > total_pages or start > end:
                messagebox.showerror("Error", 
                    f"Please enter valid contents page numbers between 1 and {total_pages}")
                return None, None
                
            return start, end
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid contents page numbers")
            return None, None

    def process_pdf(self, file_path):
        try:
            self.status_var.set("Processing PDF...")
            self.root.update()
            
            # Clear text area
            self.text_area.delete(1.0, tk.END)
            
            # Open PDF with PyMuPDF
            doc = fitz.open(file_path)
            total_pages = doc.page_count
            
            if total_pages == 0:
                raise Exception("No pages found in PDF")
            
            # Validate page ranges
            contents_start, contents_end = self.validate_contents_range(total_pages)
            start_page, end_page = self.validate_page_range(total_pages)
            
            if start_page is None:
                return
            
            # Process contents pages if specified
            if contents_start is not None and contents_end is not None:
                for page_num in range(contents_start - 1, contents_end):
                    try:
                        page = doc[page_num]
                        page_text = page.get_text(
                            "text",
                            flags=fitz.TEXT_DEHYPHENATE | fitz.TEXT_PRESERVE_WHITESPACE
                        )
                        
                        if not page_text.strip():
                            self.text_area.insert(tk.END, f"=== Page {page_num + 1} ===\n\n")
                            continue
                        
                        lines = page_text.splitlines()
                        processed_lines = []
                        
                        for line in lines:
                            leading_space = len(line) - len(line.lstrip())
                            indent = " " * leading_space
                            line = line.strip()
                            if not line:
                                processed_lines.append("")
                                continue
                            processed_lines.append(f"{indent}{line}")
                        
                        self.text_area.insert(tk.END, f"=== Page {page_num + 1} ===\n\n")
                        self.text_area.insert(tk.END, '\n'.join(processed_lines) + "\n")
                        
                    except Exception as e:
                        self.text_area.insert(tk.END, f"=== Page {page_num + 1} ===\n\n[Error: {str(e)}]\n")
                
                # After processing contents pages, analyze them and update text area
                current_text = self.text_area.get(1.0, tk.END)
                analyzed_lines = self.analyze_contents(current_text)
                if analyzed_lines is not None:
                    # Clear both text areas
                    self.text_area.delete(1.0, tk.END)
                    self.contents_area.delete(1.0, tk.END)
                    
                    # Insert contents into contents area
                    self.contents_area.insert(tk.END, '\n'.join(analyzed_lines))
                    self.contents_area.insert(tk.END, "\n\n=== END OF CONTENTS ===\n\n")
            
            # Process main text pages
            for page_num in range(start_page - 1, end_page):
                try:
                    page = doc[page_num]
                    page_text = page.get_text(
                        "text",
                        flags=fitz.TEXT_DEHYPHENATE | fitz.TEXT_PRESERVE_WHITESPACE
                    )
                    
                    if not page_text.strip():
                        # Add a header for the empty page
                        self.text_area.insert(tk.END, f"=== Page {page_num + 1} ===\n\n")
                        self.text_area.insert(tk.END, "\n")  # Add an empty line after the header
                        continue  # Continue to the next page
                    
                    lines = page_text.splitlines()
                    processed_lines = []
                    
                    for line in lines:
                        leading_space = len(line) - len(line.lstrip())
                        indent = " " * leading_space
                        line = line.strip()  # This line trims leading and trailing whitespace
                        if not line:
                            processed_lines.append("")
                            continue
                        processed_lines.append(f"{indent}{line}")
                    
                    self.text_area.insert(tk.END, f"\n=== Page {page_num + 1} ===\n\n")
                    self.text_area.insert(tk.END, '\n'.join(processed_lines) + "\n")
                    
                except Exception as e:
                    self.text_area.insert(tk.END, f"\n=== Page {page_num + 1} ===\n\n[Error: {str(e)}]\n")
            
            self.status_var.set(f"Completed processing {file_path}")
            doc.close()
            
        except Exception as e:
            error_msg = f"Error: {str(e)}\nTry a different PDF file or check if it's password protected."
            self.status_var.set(error_msg)
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, error_msg)
            print(f"Detailed error: {str(e)}")

    def upload_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not file_path:
            return
            
        # Store the file path for refining
        self.current_pdf = file_path
        
        # Process the PDF
        self.process_pdf(file_path)
        
        # Enable the refine button
        self.refine_button.config(state='normal')

    def refine_pdf(self):
        if hasattr(self, 'current_pdf'):
            self.process_pdf(self.current_pdf)
        else:
            self.status_var.set("No PDF loaded to refine")

    def mark_endnotes(self):
        """Process the current text and mark endnotes"""
        # Get current text
        current_text = self.text_area.get(1.0, tk.END)
        if not current_text.strip():
            return
            
        # Split into lines
        lines = current_text.splitlines()
        processed_lines = []
        
        # Track page sections
        current_page_lines = []
        in_page = False
        
        # Process line by line
        for line in lines:
            # Check for page markers
            if line.startswith("=== Page"):
                # Process previous page if exists
                if current_page_lines:
                    processed_lines.extend(self.process_page_endnotes(current_page_lines))
                    current_page_lines = []
                processed_lines.append(line)
                in_page = True
                continue
            
            # Collect lines for current page
            if in_page:
                current_page_lines.append(line)
            else:
                processed_lines.append(line)
        
        # Process last page
        if current_page_lines:
            processed_lines.extend(self.process_page_endnotes(current_page_lines))
        
        # Update text area
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, '\n'.join(processed_lines))

    def process_page_endnotes(self, page_lines):
        """Process a single page's lines for endnotes"""
        processed_lines = []
        # Get special characters from input, split by spaces
        special_chars = [char.strip() for char in self.special_chars.get().split()]
        
        # Find middle of page
        mid_point = len(page_lines) // 2
        in_endnote = False
        endnote_buffer = []
        
        # Process each line
        for i, line in enumerate(page_lines):
            # Skip empty lines
            if not line.strip():
                # If we were in an endnote, add the collected endnote
                if in_endnote and endnote_buffer:
                    processed_lines.append(f"<E>{''.join(endnote_buffer)}</E>")
                    endnote_buffer = []
                    in_endnote = False
                processed_lines.append(line)
                continue
            
            # Check for endnotes in second half of page
            if i >= mid_point:
                # Check if line starts with special character
                stripped_line = line.lstrip()
                if any(stripped_line.startswith(char) for char in special_chars):
                    # If we were already in an endnote, add the previous one
                    if in_endnote and endnote_buffer:
                        processed_lines.append(f"<E>{''.join(endnote_buffer)}</E>")
                    # Start new endnote
                    in_endnote = True
                    endnote_buffer = [line]
                    continue
                elif in_endnote:
                    endnote_buffer.append(f" {line.lstrip()}")
                    continue
            
            # Regular line processing
            if not in_endnote:
                processed_lines.append(line)
        
        # Handle any remaining endnote at end of page
        if in_endnote and endnote_buffer:
            processed_lines.append(f"<E>{''.join(endnote_buffer)}</E>")
        
        return processed_lines

    def remove_endnotes(self):
        """Remove all endnote-marked text from the text area"""
        try:
            # Get current text
            current_text = self.text_area.get(1.0, tk.END)
            if not current_text.strip():
                return
            
            # Split into lines
            lines = current_text.splitlines()
            processed_lines = []
            
            # Skip endnote lines and preserve other text
            i = 0
            while i < len(lines):
                line = lines[i]
                if "<E>" in line:
                    # Skip until we find the end of the endnote
                    while i < len(lines) and "</E>" not in lines[i]:
                        i += 1
                    i += 1  # Skip the line with </E>
                else:
                    processed_lines.append(line)
                    i += 1
            
            # Update text area
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, '\n'.join(processed_lines))
            
            self.status_var.set("Endnotes removed")
            
        except Exception as e:
            self.status_var.set(f"Error removing endnotes: {str(e)}")
            print(f"Error removing endnotes: {str(e)}")

    def process_page_headers(self, page_lines, previous_page_empty, max_header_length):
        """Process a single page's lines for headers"""
        processed_lines = []
        found_first_content = False
        
        for i, line in enumerate(page_lines):
            stripped_line = line.strip()
            
            # Preserve empty lines in the output
            processed_lines.append(line)  # Add the line regardless of whether it's empty or not
            
            if not stripped_line:
                continue  # Skip further processing for empty lines
            
            # Check for potential header in first non-empty line
            if not found_first_content:
                found_first_content = True
                
                # Conditions for header:
                # 1. Not the first page (previous page has content)
                # 2. Line is shorter than user-defined max header length
                # 3. Not already marked as endnote
                # 4. Not just a page number
                if (not previous_page_empty and
                    len(stripped_line) < max_header_length and  # Use user-defined value
                    not stripped_line.startswith("<E>") and
                    not stripped_line.replace(" ", "").isnumeric()  # Skip standalone numbers
                    ):
                    
                    # Preserve original indentation
                    leading_space = len(line) - len(line.lstrip())
                    indent = " " * leading_space
                    processed_lines[-1] = f"{indent}<H>{stripped_line}</H>"  # Replace the last entry with the header
        
        return processed_lines

    def mark_headers(self):
        """Process the current text and mark headers"""
        try:
            # Get current text
            current_text = self.text_area.get(1.0, tk.END)
            if not current_text.strip():
                return
            
            # Get user-defined max header length
            max_header_length = int(self.max_header_length_entry.get())
            
            # Split into lines
            lines = current_text.splitlines()
            processed_lines = []
            
            # Track pages and their content
            current_page_lines = []
            previous_page_empty = True
            in_page = False
            
            # Second pass: process headers
            for line in lines:
                # Check for page markers
                if line.startswith("=== Page"):
                    # Process previous page if exists
                    if current_page_lines:
                        processed_lines.extend(
                            self.process_page_headers(
                                current_page_lines,
                                previous_page_empty,
                                max_header_length
                            )
                        )
                        # Update previous_page_empty based on current_page_lines
                        non_empty_count = len([l for l in current_page_lines if l.strip()])
                        previous_page_empty = non_empty_count <= 2  # Set to False if more than 2 non-empty lines
                        current_page_lines = []
                    
                    processed_lines.append(line)
                    in_page = True
                    continue
                
                # Collect lines for current page
                if in_page:
                    current_page_lines.append(line)
                else:
                    processed_lines.append(line)
            
            # Process last page
            if current_page_lines:
                processed_lines.extend(
                    self.process_page_headers(
                        current_page_lines,
                        previous_page_empty,
                        max_header_length
                    )
                )
            
            # Update text area
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, '\n'.join(processed_lines))
            
            self.status_var.set("Headers marked")
            
        except Exception as e:
            self.status_var.set(f"Error marking headers: {str(e)}")
            print(f"Detailed error: {str(e)}")

    def remove_headers(self):
        """Remove all header-marked text from the text area"""
        try:
            # Get current text
            current_text = self.text_area.get(1.0, tk.END)
            if not current_text.strip():
                return
            
            # Split into lines
            lines = current_text.splitlines()
            processed_lines = []
            
            # Remove lines that contain <H> tags
            for line in lines:
                if "<H>" not in line:  # Check if the line does not contain a header tag
                    processed_lines.append(line)
            
            # Update text area with lines that are not headers
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, '\n'.join(processed_lines))
            
            self.status_var.set("Headers removed")
            
        except Exception as e:
            self.status_var.set(f"Error removing headers: {str(e)}")
            print(f"Error removing headers: {str(e)}")

    def mark_page_numbers(self):
        """Identify lines with only digits or special characters and mark them as <N>"""
        try:
            # Get current text
            current_text = self.text_area.get(1.0, tk.END)
            if not current_text.strip():
                return
            
            # Split into lines
            lines = current_text.splitlines()
            processed_lines = []
            
            for line in lines:
                stripped_line = line.strip()
                # Check if the line contains only digits or special characters
                if re.fullmatch(r'[\d\W]+', stripped_line):  # Matches digits and non-word characters
                    processed_lines.append(f"<N>{stripped_line}</N>")  # Mark as page number
                else:
                    processed_lines.append(line)  # Keep the line as is
            
            # Update text area with marked page numbers
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, '\n'.join(processed_lines))
            
            self.status_var.set("Page numbers marked")
            
        except Exception as e:
            self.status_var.set(f"Error marking page numbers: {str(e)}")
            print(f"Error marking page numbers: {str(e)}")

    def remove_page_numbers(self):
        """Remove lines marked as <N> from the text area"""
        try:
            # Get current text
            current_text = self.text_area.get(1.0, tk.END)
            if not current_text.strip():
                return
            
            # Split into lines
            lines = current_text.splitlines()
            processed_lines = []
            
            for line in lines:
                # Check if the line contains <N>
                if "<N>" not in line:
                    processed_lines.append(line)  # Keep the line as is
            
            # Update text area without the marked page numbers
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, '\n'.join(processed_lines))
            
            self.status_var.set("Page numbers removed")
            
        except Exception as e:
            self.status_var.set(f"Error removing page numbers: {str(e)}")
            print(f"Error removing page numbers: {str(e)}")

    def analyze_contents(self, text_content):
        """Analyze the text content for table of contents"""
        try:
            # Clear previous contents table
            self.contents_table = []
            
            # Split into lines
            lines = text_content.splitlines()
            tagged_line_counter = 0
            processed_lines = []
            
            # Process all lines
            for i in range(len(lines)):
                line = lines[i]
                
                # Skip page marker lines and empty lines
                if line.startswith("=== Page") or not line.strip():
                    continue
                
                # Check if line ends with a number
                if re.search(r'\d+$', line.strip()):
                    merged_line = line
                    
                    # If we've already tagged some lines, try to merge with previous untagged lines
                    if tagged_line_counter > 0:
                        # Start from the most recent line and work backwards
                        j = len(processed_lines) - 1
                        merge_content = []
                        
                        # Keep going backwards until we hit a tagged line or the start
                        while j >= 0:
                            prev_line = processed_lines[j]
                            # Stop if we hit a tagged line
                            if "<C>" in prev_line:
                                break
                            merge_content.insert(0, prev_line)
                            j -= 1
                        
                        # Remove the merged lines from processed_lines
                        processed_lines = processed_lines[:j + 1]
                        
                        # If we found lines to merge, combine them with the current line
                        if merge_content:
                            merged_line = " ".join(merge_content + [line.strip()])
                    
                    # Tag the line (whether merged or not) and increment counter
                    processed_lines.append(f"<C>{merged_line.strip()}")
                    tagged_line_counter += 1
                else:
                    # If not a numbered line, add as-is
                    processed_lines.append(line)
            
            # Clean up consecutive dots/spaces before numbers in processed lines
            cleaned_lines = []
            for line in processed_lines:
                if "<C>" in line:
                    # Extract the number at the end and remove <C> tags for processing
                    line_without_tags = line.replace("<C>", "").replace("</C>", "")
                    match = re.search(r'(.*?)[.…\s]+(\d+)\s*$', line_without_tags)
                    if match:
                        text_part = match.group(1).strip()
                        number_part = match.group(2)
                        cleaned_line = f"<C>{text_part} {number_part}"
                        cleaned_lines.append(cleaned_line)
                        
                        # Add to contents table
                        self.contents_table.append({
                            'text': text_part,
                            'page': int(number_part)
                        })
                    else:
                        cleaned_lines.append(line)
                else:
                    cleaned_lines.append(line)
            
            # Remove <C> tags from the beginning of lines
            final_lines = [line.replace("<C>", "") if line.startswith("<C>") else line for line in cleaned_lines]
            
            return final_lines
            
        except Exception as e:
            print(f"Error analyzing contents: {str(e)}")
            return None

def main():
    root = tk.Tk()
    app = BookSummaryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 