from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
import pandas as pd
import re
import os

app = Flask(__name__)

def convert_pdf_to_excel(input_path, output_path, extraction_method, format_in, word_divider, number_of_line, words_per_line=5, empty_lines_input=10, each_word_in='y', custom_entry='lorem'):
    def open_pdf(input_path):
        text=''
        reader=PdfReader(input_path)
        for page in reader.pages:
            text+=page.extract_text()
        return text
    
    if extraction_method=='column' or extraction_method=='row' or extraction_method=='space' or extraction_method=='word':    
        text=open_pdf(input_path)    
        words = re.findall(r'\S+', text)
        segments = [' '.join(words[i:i+word_divider]) for i in range(0, len(words), word_divider)]
        segment_count = len(segments) // number_of_line
        if format_in=='column format':
            data = {'Column{}'.format(i+1): segments[i:i+segment_count] for i in range(number_of_line)}
            df = pd.DataFrame(data)
            df.to_excel(output_path, index=False)
            return df
        elif format_in=='row format':
            data = {'Column{}'.format(i+1): segments[i:i+segment_count] for i in range(number_of_line)}
            df_row= pd.DataFrame(data)
            row_format=df_row.transpose()
            row_format.to_excel(output_path, index=False)
            return row_format
    
    elif extraction_method=='line':
        def extract_text_from_pdf(pdf_file_path):
            text = ""
            with open(pdf_file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text().replace('\n', ' ')
            return text

        def format_text(text, words_per_line, empty_lines_after):
            lines = text.split('\n')
            formatted_text = ''
            word_count = 0
            for line in lines:
                words = line.strip().split()
                for word in words:
                    formatted_text += word + ' '
                    word_count += 1
                    if word_count == words_per_line:
                        formatted_text += '\n'
                        word_count = 0
                        empty_lines_after -= 1
                        if empty_lines_after == 0:
                            formatted_text += '\n'
                            empty_lines_after = empty_lines_input
                if word_count == 0:
                    formatted_text += '\n'
                    empty_lines_after -= 1
                    if empty_lines_after == 0:
                        formatted_text += '\n'
                        empty_lines_after = empty_lines_input
            return formatted_text

        extracted_text = extract_text_from_pdf(input_path)

        formatted_text = format_text(extracted_text, words_per_line, empty_lines_input)

        rows = formatted_text.strip().split('\n')

        if each_word_in == 'y':
            df = pd.DataFrame([row.split() for row in rows])
        else:
            df = pd.DataFrame([row for row in rows])

        df.to_excel(output_path, index=False, header=False)
        return df

    elif extraction_method=='exact':
        reader = PdfReader(input_path)
        all_text = []
        for page in reader.pages:
            text = page.extract_text()
            all_text.extend(text.split('\n'))

        data = {'Text': all_text}
        df = pd.DataFrame(data)
        df.to_excel(output_path, index=False)
        return df

    elif extraction_method == 'custom':
        reader = PdfReader(input_path)
        anything = custom_entry

        output_data = []

        for page in reader.pages:
            text = page.extract_text().lower()
            lines = text.split('\n') 

            for line in lines:
                match_indices = [m.start() for m in re.finditer(re.escape(anything), line)]
                if match_indices:
                    parts = []
                    last_index = 0
                    for index in match_indices:
                        parts.append(line[last_index:index])
                        parts.append(anything)
                        last_index = index + len(anything)
                    parts.append(line[last_index:])
                    output_data.extend(parts)
                else:
                    output_data.append(line)
        if format_in=='row format':
            df = pd.DataFrame(output_data, columns=['Text'])
            df.to_excel(output_path, index=False)
            return df
        elif format_in == 'column format':
            df = pd.DataFrame(output_data, columns=['Text'])
            df_transpose=df.transpose()
            df_transpose.to_excel(output_path, index=False)
            return df_transpose

@app.route('/convert_pdf_to_excel', methods=['POST'])
def pdf_to_excel_conversion():
    print(request.files)
    input_file = request.files['input_path']  # Use 'input_file' as the key for the uploaded file
    input_path = 'temp.pdf'  # Save the uploaded file temporarily
    input_file.save(input_path)  # Save the uploaded file to disk
    print(input_path)
    output_path = request.form['output_path']
    extraction_method = request.form['extraction_method']
    format_in = request.form['format_in']
    word_divider = int(request.form['word_divider'])
    number_of_line = int(request.form['number_of_line'])
    words_per_line = int(request.form.get('words_per_line', 5))
    empty_lines_input = int(request.form.get('empty_lines_input', 10))
    each_word_in = request.form.get('each_word_in', 'y')
    custom_entry = request.form.get('custom_entry', 'lorem')


    
    print("Input path:", input_path)
    print("Output path:", output_path)
    print("Extraction method:", extraction_method)
    print("Format:", format_in)
    print("Word divider:", word_divider)
    print("Number of lines:", number_of_line)
    print("Words per line:", words_per_line)
    print("Empty lines input:", empty_lines_input)
    print("Each word in:", each_word_in)
    print("Custom entry:", custom_entry)
    
    
    result_df=convert_pdf_to_excel(input_path, output_path, extraction_method, format_in, word_divider, number_of_line, words_per_line, empty_lines_input, each_word_in, custom_entry)

    os.remove(input_path)
    print("Result DataFrame:", result_df)

    return jsonify({'message': 'Conversion successful.', 'output_path': output_path, 'dataframe': result_df.to_json()}), 200

if __name__ == '__main__':
    app.run(debug=True)
