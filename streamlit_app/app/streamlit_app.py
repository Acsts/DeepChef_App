#Logo by gregoire@gm-drone.fr
import streamlit as st
from streamlit_lottie import st_lottie
import pandas as pd
import numpy as np
import requests
from PIL import Image
from PIL.ImageOps import exif_transpose
import time
import base64
import io

def page_initializer(clear = False):
    if 'ingredients_photos' not in st.session_state or clear == True:
        st.session_state.ingredients_photos = []
    if 'text_input_content' not in st.session_state or clear == True:
        st.session_state.text_input_content = ""
    if 'ingredients' not in st.session_state or clear == True:
        st.session_state.ingredients = np.array([])
    if 'ingredients_selection' not in st.session_state or clear == True:
        st.session_state.ingredients_selection = []
    if 'api_output' not in st.session_state or clear == True:
        st.session_state.api_output = []

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def header():
    # Page config
    st.set_page_config(
    page_title="DeepChef",
    page_icon="🥬",
    layout="centered",
    initial_sidebar_state="expanded"
    )
    # Page logo
    logo_image = Image.open('img/DEEPCHEF_PAYSAGE-LARGE.png')
    st.image(logo_image, output_format="PNG")
    # Page title and introduction
    col_intro, col_lottie = st.columns([4,1])
    with col_intro:
        st.text("")
        st.text("")
        st.markdown("##### Welcome to DeepChef, your favorite kitchen help")
        st.markdown("###### All you needed was a pinch of inspiration!💡")
    with col_lottie:
        lottie_cook = load_lottieurl("https://assets8.lottiefiles.com/packages/lf20_5e4mlcwz.json")
        st_lottie(lottie_cook,height=150,width=150,speed=1)
    st.markdown("---")

def photos_uploader(): 
    ### Displays a file uploader and stores in session_state a list of photos each in numpy.array format (list updated at each file add/removal)
    # Photos collected from the uploader
    img_files_buffer = st.file_uploader("Upload photos of your ingredidents:",
    #type = <array of types depending of the inputs accepted by the model>,
    accept_multiple_files = True
    )
    if len(img_files_buffer)!=0:
        # Store the uploaded photos in the session_state
        st.session_state.ingredients_photos = img_files_buffer
        # Display previews of the uploaded photos
        for img_file in img_files_buffer:
            # Auto-rotate the photo taking into account its Exif tag
            img = exif_transpose(Image.open(img_file))
            # Show photo preview
            st.image(img, width = 50)

def ingredients_from_predictions(img_files_list):
    ### Input : list of image files to feed to the classification / detection model
    ### Ouptut : list of ingredients names predicted by the model
    output_ingredients_list = np.array([]) # We use a ndarray type keep a 1-dimensional list even if we append lists to it 
    url = 'https://deepchef-api.herokuapp.com/detect'
    for i, img_file in enumerate(img_files_list):
        # Preapring files for the post request in the format (file name, file content in bytes)
        files = {'img_file': (img_file.name, img_file.getvalue())}
        # Getting predictions from the model API and storing the results in the output list
        try:
            r = requests.post(url, files=files)
            # output_ingredients_list = np.append(output_ingredients_list, r.json()["prediction"])
            output_ingredients_list = np.append(output_ingredients_list, r.json()["predictions"])
            if len(r.json()["predictions"])!=0:
                predictions_image = exif_transpose(Image.open(io.BytesIO(base64.b64decode(r.json()["predictions_image"])))) # Decoding the b64 string we obtained from the model
                st.success(f"Ingredients detected on image {i+1} : {enumeration_phrase(list(set(r.json()['predictions'])))}")
                st.image(predictions_image)
            else:
                st.write(f"No ingredients detected on image {i+1}.")
                st.image(exif_transpose(Image.open(img_file)))
        except requests.exceptions.ConnectionError:
            st.write("Failed to connect to the ingredients detection API")
    return output_ingredients_list

def ingredients_from_text_inputs():
    # Adding each comma-separated ingredient name to the ingredients list
    if st.session_state.text_input_content.strip() != "":
        st.session_state.ingredients = np.append(st.session_state.ingredients, [el.strip() for el in st.session_state.text_input_content.split(',')])
    # Reset the "text_input" session state as empty string
    st.session_state.text_input_content = ""

def clear_ingredients_list():
    st.session_state.ingredients = np.array([])

def enumeration_phrase(listing):
    return f"{', '.join([s.capitalize() for s in listing][:-1])} and " * (len(listing)>1) + str(listing[-1].capitalize())

def get_recipe_by_ingredients(ingredients):
    response = requests.get("https://api.spoonacular.com/recipes/findByIngredients?ingredients={}&number=5&apiKey=b11c72687e7b45418f7c2a6c55efe798".format(ingredients))
    result = response.json()
    if len(result)!=0:
        result_df = pd.json_normalize(result)
        ingredient_feature_to_extract = 'name'
        result_df[f"usedIngredients_{ingredient_feature_to_extract}s"]=result_df['usedIngredients'].apply(lambda x : [x[ingredient_idx][ingredient_feature_to_extract] for ingredient_idx in range(len(x))])
        result_df[f'missedIngredients_{ingredient_feature_to_extract}s']=result_df['missedIngredients'].apply(lambda x : [x[ingredient_idx][ingredient_feature_to_extract] for ingredient_idx in range(len(x))])
        result_df[f'unusedIngredients_{ingredient_feature_to_extract}s']=result_df['unusedIngredients'].apply(lambda x : [x[ingredient_idx][ingredient_feature_to_extract] for ingredient_idx in range(len(x))])
    else:
        result_df = []
    return result_df

def recipe_summary(recipe_id):
    response = requests.get("https://api.spoonacular.com/recipes/{}/summary?&apiKey=b11c72687e7b45418f7c2a6c55efe798".format(recipe_id))
    summary = response.json()['summary']
    return summary

def debug_inner_state():
    clear_session_states = st.button("CLEAR VARIABLES", on_click = page_initializer, kwargs = {'clear' : True})
    st.write(st.session_state)


###########################
######## MAIN CODE ########
###########################

if __name__ == '__main__':

    header()
    page_initializer()

    #########
    # GETTING PHOTOS AND TEXT AS INPUTS
    col_photos, col_text = st.columns(2)
    with col_photos:
        st.markdown("##### Show me what you've got")
        photos_uploader()
        submit_photos = st.button("Submit photos")
        if submit_photos:
            st.session_state.ingredients = np.append(st.session_state.ingredients, ingredients_from_predictions(st.session_state.ingredients_photos))
            st.session_state.ingredients = st.session_state.ingredients.flatten()
    with col_text:
        st.markdown("##### Or just write it down")
        text_input = st.text_input("Please tell me what's in your fridge 🍽",help = 'Please insert your ingredients separated by commas',
        key = 'text_input_content',
        on_change = ingredients_from_text_inputs
        )
    st.markdown(f"###### You have: {', '.join(set([name.capitalize() for name in st.session_state.ingredients.tolist()]))}")
    if len(st.session_state.ingredients)!=0:
        clear_ingredients = st.button("Clear ingredients list", on_click = clear_ingredients_list)

    st.markdown("---")
    #########

    #########
    # CALLING THE API AND GET THE RECIPES
    api_call = st.button("READY TO COOK !! 👨‍🍳️")
    # Calling the API only if the api_call button is clicked AND the uniques ingredients list has been updated since the last api_call click
    if api_call and (sorted(st.session_state.ingredients.tolist()) != sorted(st.session_state.ingredients_selection)):
        st.session_state.ingredients_selection = sorted(st.session_state.ingredients.tolist())
        st.session_state.api_output = get_recipe_by_ingredients(','.join(st.session_state.ingredients_selection))
        with st.spinner('Wait for it...'):
            time.sleep(1)
            st.success('Here you are!')
    # Displaying the recipe propositions
    if len(st.session_state.ingredients_selection)!=0:
        if len(st.session_state.api_output)!=0:
            col1, col2 = st.columns(2)
            with col1:
                #st.write("Your ingredients :", ','.join(st.session_state.ingredients))
                st.markdown("**1️⃣ Our chef suggests:**")
                main_recipe_box = st.selectbox("Select the recipe that best suits you:", st.session_state.api_output["title"].sort_values().unique())
                main_recipe = st.session_state.api_output[st.session_state.api_output["title"]==main_recipe_box].reset_index()
                main_recipe_photo = main_recipe['image'][0]
                st.image(main_recipe_photo, width = 350)
            with col2:
                st.markdown("**2️⃣ The Ingredients to make it:**")
                used_ingredients = main_recipe['usedIngredients_names'][0]
                missed_ingredients = main_recipe['missedIngredients_names'][0]
                leftovers_list = list(set(main_recipe['unusedIngredients_names'][0]))
                
                st.write("🥗 You already have " + enumeration_phrase(used_ingredients) + '.')
                if len(missed_ingredients)!=0: 
                    st.write("🛒 You need to buy " + enumeration_phrase(missed_ingredients) + '.')
                else:
                    st.write("...and you need nothing more !! 🙌 ")
                # Leftovers recipe suggestion
                st.markdown("---") 
                if len(leftovers_list)!=0:
                    st.write(f"Oh wait! And after that, you could use {enumeration_phrase(leftovers_list)} in another recipe such as :")
                    leftovers_recipes = get_recipe_by_ingredients(','.join(leftovers_list))
                    leftovers_recipe_photo = leftovers_recipes['image'][0]
                    leftovers_recipe_name = leftovers_recipes['title'][0]
                    st.write(leftovers_recipe_name)
                    st.image(leftovers_recipe_photo, width = 150)

            st.markdown("---") 

            #Recipe expander
            main_recipe_id = main_recipe['id'][0]
            recipe_instructions = recipe_summary(main_recipe_id)
            with st.expander("Get the instructions! 👨‍🍳"):
                st.markdown("#### Here are the instructions for your recipe : ")
                st.markdown(recipe_instructions, unsafe_allow_html=True)
            #Here we need to insert the recipe guidance from recupe
        else:
            st.write("Hmm, no recipe found for this ingredients list... Are you sure they're real ingredients ?")
    st.markdown("---") 
    #Contact form
    with st.expander("Get in Touch With us 📫"):
        contact_form = """
        <form action="https://formsubmit.co/deepfoodapp@gmail.com" method="POST">
            <input type="hidden" name="_captcha" value="false">
            <input type="text" name="name" placeholder="Your name" required>
            <input type="email" name="email" placeholder="Your email" required>
            <textarea name="message" placeholder="Your message here"></textarea>
            <button type="submit">Send</button>
        </form>
        """
        st.markdown(contact_form, unsafe_allow_html=True)
        # Use Local CSS File
        def local_css(file_name):
            with open(file_name) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        local_css("style/style.css")
    col3, col4 = st.columns([1,4])
    with col3:
        #Page logo
        image = Image.open('img/DEEPCHEF3.png')
        st.image(image, output_format="PNG",width=145)
    with col4:
        ### Footer 
        st.markdown("""     
                DeepChef has been made with ❤️ by [Lea Boussekeyt](https://github.com/leaboussekeyt), [Quentin Gottafray](https://github.com/Quentin50)  [Baptiste Eluard](https://github.com/baptel), [Antoine Costes](https://github.com/Acsts) and [Christopher Gbezo](https://github.com/cgbezo)
            """)


    #debug_inner_state()