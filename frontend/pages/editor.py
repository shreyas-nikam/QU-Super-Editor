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

class Editor:
    def __init__(self):
        st.session_state.selected_application = None
        st.session_state.selected_file = None
        st.session_state.content = None

        st.session_state.selected_application_button_pressed = False
        st.session_state.selected_file_button_pressed = False
        st.session_state.save_button_pressed = False
            
    def render(self):
        st.title("Editor")

        # Application select functionality
        applications = get_folders_from_s3()
        st.write("Select an application:")
        application_selectbox_col, application_selectbutton_col = st.columns([3, 1])
        with application_selectbox_col:
            st.session_state.selected_application = st.selectbox("Select an application", applications, label_visibility="collapsed", on_change=lambda: st.session_state.update({"selected_application_button_pressed": False}))

        with application_selectbutton_col:
            select_application_button_pressed = st.button("Get Files", use_container_width=True, type="primary")
        
        st.divider()


        # File select functionality
        if select_application_button_pressed or st.session_state.selected_application_button_pressed:    
            st.session_state.selected_application_button_pressed = True
            files = get_files_by_folder_from_s3()
            files = files.get(st.session_state.selected_application, [])
            st.write("Select a file:")
            file_selectbox_col, file_selectbutton_col = st.columns([3, 1])
            with file_selectbox_col:
                st.session_state.selected_file = st.selectbox("Select a file", [file[file.rindex("/")+1:] for file in files], index=0, key="file_index", label_visibility="collapsed", on_change=lambda: st.session_state.update({"selected_file_button_pressed": False}))
            
            with file_selectbutton_col:
                select_file_button_pressed = st.button("Get Content", use_container_width=True, type="primary")
    
            st.divider()

            if select_file_button_pressed or st.session_state.selected_file_button_pressed:
                st.session_state.selected_file_button_pressed = True
                key = st.session_state.selected_application +"/"+ st.session_state.selected_file
                content = get_file_content_from_s3(key)
            
                # if the file type is json, convert the content string to a dictionary. and display the key value pairs as separate inputs. Create three columns. One for the key, the second for the value and the third for checking if there are any mandatory inputs in the value. if there are mandatory inputs in the value, they should be displayed as checkboxes in the third column. only if all the checkboxes are ticked, they can save they file. the checkboxes should be ticked automatically by reading the value/
                if key.endswith(".json"):
                    title_content_col, title_value_col, title_mandatory_col = st.columns([1, 3, 1])
                    with title_content_col:
                        st.write("**Prompt Title**")
                    with title_value_col:
                        st.write("**Prompt Value**")
                    with title_mandatory_col:
                        st.write("**Mandatory Fields**")
                    st.divider()
                    try:
                        content = json.loads(content)
                    except json.JSONDecodeError:
                        st.error("Invalid JSON content")
                        return
                    
                    index = 0
                    for content_key in list(content.keys()):
                        content_value = content[content_key]
                        content_col, value_col, mandatory_col = st.columns([1, 3, 1])
                        index+=1
                        # display all the keys
                        with content_col:
                            st.write(content_key.replace("_", " ").title())
                        # display all the values
                        with value_col:
                            new_value = st.text_area("Value", content_value.strip(), key=index, height=200, label_visibility="collapsed")
                        # display all the mandatory fields
                        with mandatory_col:
                            mandatory_fields = _get_mandatory_fields(content_value)
                            mandatory_checkboxes = []
                            for field in mandatory_fields:
                                checkbox = st.checkbox(field, disabled=True, value=field in new_value, key=f"{index}_{field}_checkbox")
                                mandatory_checkboxes.append(checkbox)
                            if all(mandatory_checkboxes):
                                save_button_pressed = st.button("Save", type="primary", key=f"{index}_save_button")
                                if save_button_pressed:
                                    content[content_key] = new_value
                                    save_file_content_to_s3(json.dumps(content), key)
                                    st.success("Prompt updated and saved!")
                        st.divider()
                        
                