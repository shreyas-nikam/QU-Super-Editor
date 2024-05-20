import streamlit as st
from backend.s3 import get_folders_from_s3, get_files_by_folder_from_s3, get_file_content_from_s3, save_file_content_to_s3
import json
import re

def _get_mandatory_fields(value: str) -> list[str]:
    # Functionality to get the mandatory fields from the value
    mandatory_fields = re.findall(r"\{(.*?)\}", value)
    # add the curly braces to the fields
    mandatory_fields = [f"{{{field}}}" for field in mandatory_fields]
    return mandatory_fields


def render():
    st.title("Editor")

    # Application select functionality
    applications = get_folders_from_s3()
    application_selectbox_col, application_selectbutton_col = st.columns([3, 1])
    with application_selectbox_col:
        selected_application = st.selectbox("Select an application", applications)

    with application_selectbutton_col:
        select_application_button_pressed = st.button("Get Files", use_container_width=True, type="primary")
    
    st.divider()


    # File select functionality
    if select_application_button_pressed:    
        files = get_files_by_folder_from_s3()
        files = files.get(selected_application, [])
        file_selectbox_col, file_selectbutton_col = st.columns([3, 1])
        with file_selectbox_col:
            selected_file = st.selectbox("Select a file", [file[file.rindex("/")+1:] for file in files], index=0, key="file_index")
        
        with file_selectbutton_col:
            select_file_button_pressed = st.button("Get Content", use_container_width=True, type="primary")
  
        st.divider()

        if select_file_button_pressed:
            key = selected_application + selected_file
            content = get_file_content_from_s3(key)
        
            # if the file type is json, convert the content string to a dictionary. and display the key value pairs as separate inputs. Create three columns. One for the key, the second for the value and the third for checking if there are any mandatory inputs in the value. if there are mandatory inputs in the value, they should be displayed as checkboxes in the third column. only if all the checkboxes are ticked, they can save they file. the checkboxes should be ticked automatically by reading the value/
            if key.endswith(".json"):
                content = json.loads(content)
                content_col, value_col, mandatory_col = st.columns([1, 1, 1])
                for content_key, content_value in content.items():
                    # display all the keys
                    with content_col:
                        content_key = st.write(content_key)
                    # display all the values
                    with value_col:
                        new_value = st.text_area("Value", content_value)
                    # display all the mandatory fields
                    with mandatory_col:
                        mandatory_fields = _get_mandatory_fields(content_value)
                        mandatory_checkboxes = []
                        for field in mandatory_fields:
                            checkbox = st.checkbox(field, disabled=True, value=field in content_value)
                            mandatory_checkboxes.append(checkbox)
                        if all(mandatory_checkboxes):
                            save_button_pressed = st.button("Save", type="primary")
                            if save_button_pressed:
                                content[key] = new_value
                                save_file_content_to_s3(json.dumps(content), key)
                                st.success("File saved successfully!")
                    st.divider()
                    
            