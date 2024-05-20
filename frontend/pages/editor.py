import streamlit as st
from backend.s3 import get_folders_from_s3, get_files_by_folder_from_s3, get_file_content_from_s3, save_file_content_to_s3
import json
import re


class Editor:
    def __init__(self):
        st.session_state.selected_application = None
        st.session_state.selected_file = None
        st.session_state.content = None

        st.session_state.selected_application_button_pressed = False
        st.session_state.selected_file_button_pressed = False
        st.session_state.save_button_pressed = False


    def _display_json(self, key: str):
        if type(st.session_state.content)!=dict:
            try:
                st.session_state.content = json.loads(st.session_state.content)
            except json.JSONDecodeError:
                st.error("Invalid JSON content")
                return
            
        
        prompts = st.session_state.content['prompts']
        for prompt in prompts:
            title_description_col, content_col, mandatory_output_col = st.columns([1, 3, 2])
            id = prompt['id']
            title = prompt['title'].replace("_", " ")
            description = prompt['description']
            prompt_content = prompt['prompt_content']
            fields = prompt['fields']
            output_format = prompt['output_format'.upper()]

            with title_description_col:
                st.write("Title:")
                st.write(f"**{title}**")
                st.write("Description:")
                st.write(description)
            with content_col:
                old_value = prompt_content
                st.write("Prompt:")
                new_value = st.text_area("Value", old_value.strip(), key=f"{id}_content_input", height=400, label_visibility="collapsed") 
            with mandatory_output_col:
                if fields!=[]:
                    st.write("Mandatory Fields:")
                checkboxes = []
                for field in fields:
                    field_name = field['name']
                    field_label = field['label']
                    field_descripition = field['description']
                    field_checkbox = st.checkbox(f"{field_label} ({field_name})", disabled=True, value=field_name in new_value, key=f"{id}_{field_name}_checkbox", help=field_descripition)
                    checkboxes.append(field_checkbox)
                if all(checkboxes):
                    save_button_pressed = st.button("Save", type="primary", key=f"{id}_save_button")
                    if save_button_pressed:
                        # find the prompt with the id and update the prompt_content with the new value
                        for i in range(len(st.session_state.content['prompts'])):
                            if st.session_state.content['prompts'][i]['id'] == id:
                                st.session_state.content['prompts'][i]['prompt_content'] = new_value
                                break
                        save_file_content_to_s3(json.dumps(st.session_state.content), key)
                        st.success("Prompt updated and saved!")
                st.divider()
                st.write("Output Format:")
                st.text(f"{output_format}")
            st.divider()

            
    def render(self):
        st.header("Editor", divider='blue')

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
                # if the file type is json, convert the content string to a dictionary. and display the key value pairs as separate inputs. Create three columns. One for the key, the second for the value and the third for checking if there are any mandatory inputs in the value. if there are mandatory inputs in the value, they should be displayed as checkboxes in the third column. only if all the checkboxes are ticked, they can save they file. the checkboxes should be ticked automatically by reading the value/
                if key.endswith(".json"):
                    try:
                        st.session_state.content = get_file_content_from_s3(key)
                        st.session_state.content = json.loads(st.session_state.content)
                        self._display_json(key)
                    except json.JSONDecodeError:
                        st.error("Invalid JSON content")
                        return
                    
                    
                _, reset_button_col = st.columns([3, 1])
                with reset_button_col:
                    reset_button = st.button("Reset All Fields", type="secondary", use_container_width=True, key="reset_button")
                    if reset_button:
                        st.session_state.content = json.loads(get_file_content_from_s3("backup/" + st.session_state.selected_application + "/" + st.session_state.selected_file))
                        save_file_content_to_s3(json.dumps(st.session_state.content), key)
                        print(st.session_state)
                        st.rerun()
                            
                    