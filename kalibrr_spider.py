from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import csv

#Input driver location
driver_location = r"\Desktop\chromedriver_win32\chromedriver"

#Input UN and PW - Recruiter Account
email = ""
password = ""
search_text = "talent acquisition"
save_file = "kalibrr.csv"
max_number = 150
driver = None
implicit_wait_time = 10
small_wait_time = 3


def main():
    global driver
    driver = webdriver.Chrome(driver_location)
    driver.implicitly_wait(implicit_wait_time)
    login()
    time.sleep(5)
    profile_links = get_profile_links()
    #profile_links = ["https://www.kalibrr.ph/recruiter/sourcing/637592",
    #                 "https://www.kalibrr.ph/recruiter/sourcing/371376"]
    my_data = get_my_data(profile_links)
    save_my_data(my_data)


def save_my_data(my_data):
    with open(save_file, "w", newline="\n", encoding="utf-8") as normal_writer:
        csv_writer = csv.writer(normal_writer)
        csv_writer.writerows(my_data)


def get_my_data(profile_links):
    global max_number
    labels = ["NAME", "LINK", "WORK EXPERIENCE / STATUS", "WORK HISTORY", "COMPANY", "DESCRIPTION",
              "COURSE", "EDUCATION", "SKILLS"]
    my_data = [labels]
    profiles_scraped = 0
    for profile_link in profile_links:
        if max_number == profiles_scraped:
            break
        current_data = get_data_for_profile(profile_link)
        if current_data is not None:
            my_data.extend(current_data)
        profiles_scraped += 1
    return my_data


def get_data_for_profile(profile_link):
    print("scraping link: {}".format(profile_link))
    global driver
    driver.get(profile_link)
    wait_for_page_load()
    time.sleep(small_wait_time)
    data_ls = []
    full_name = get_full_name()
    data_ls.append([full_name])
    data_ls.append([profile_link])
    experience = get_experience()
    data_ls.append([experience])
    work_histories = get_work_histories()
    data_ls.append(work_histories[0])
    data_ls.append(work_histories[1])
    data_ls.append(work_histories[2])
    educations = get_educations()
    data_ls.append(educations[0])
    data_ls.append(educations[1])
    skills = get_skills()
    data_ls.append(skills)
    final_index = 0
    final_list = []
    while 1:
        end = True
        current_list = []
        for ind, _ in enumerate(data_ls):
            cur_elem = get_from_my_list(data_ls[ind], final_index)
            if cur_elem != "":
                end = False
            current_list.append(cur_elem)
        final_index += 1
        if end:
            break
        else:
            final_list.append(current_list)
    return final_list


def get_from_my_list(ls, ind):
    if ind >= len(ls):
        return ""
    return ls[ind]


def get_skills():
    data = driver.find_elements_by_css_selector("ul.list-col-sm-6 li")
    new_data = [elem.text.encode("ascii", "ignore").decode("utf-8")for elem in data]
    return new_data


def get_educations():
    try:
        data = driver.find_elements_by_css_selector("div.panel-list-item.kb-candidate-section")[1]. \
            find_elements_by_css_selector("div.profile-details-item")
        new_data = [elem.text.encode("ascii", "ignore").decode("utf-8") for elem in data]
        courses = list()
        university_names = list()
        for ind, elem in enumerate(new_data):
            if ind % 2 == 0:
                courses.append(elem)
            else:
                university_names.append(elem)
        return [courses, university_names]
    except Exception:
        return [[], []]


def get_work_histories():
    try:
        data = driver.find_element_by_css_selector("div.panel-list-item.kb-candidate-section").\
            find_elements_by_css_selector("div.profile-details-item")
        new_data = [elem.text.encode("ascii", "ignore").decode("utf-8") for elem in data]
        names = list()
        companies = list()
        descriptions = list()
        for ind, elem in enumerate(new_data):
            if ind % 3 == 0:
                names.append(elem)
            elif ind % 3 == 1:
                companies.append(elem)
            else:
                disc_ls = elem.split("\n")
                tmp_ls = [elem.strip() for elem in disc_ls if elem != ""]
                descriptions.extend(tmp_ls)
                ls_to_add = [""] * (len(tmp_ls) - 1)
                names.extend(ls_to_add)
                companies.extend(ls_to_add)
        return [names, companies, descriptions]
    except Exception:
        return [[], [], []]


def get_experience():
    try:
        experience = driver.find_element_by_css_selector("ul.list-horizontal").text
        experience = experience.replace("\n", ". ")
        return experience
    except Exception:
        return ""


def get_full_name():
    try:
        return driver.find_element_by_css_selector("h1.candidate-name").text
    except Exception:
        return ""


def get_profile_links():
    global driver
    # to check if login was successful
    driver.find_element_by_class_name("mi-notifications")
    driver.get("https://www.kalibrr.ph/recruiter/sourcing?text_search=" + search_text)
    profile_links = list()
    page_index = 1
    while 1:
        print("Getting profile links from page {}".format(page_index))
        wait_for_page_load()
        time.sleep(2*small_wait_time)
        load_more_button = driver.find_element_by_css_selector("button.btn-link")
        if not load_more_button.is_displayed():
            break
        load_more_button.send_keys(Keys.RETURN)
        page_index += 1
    tmp_profile_links = driver.find_elements_by_css_selector("div.cc-picture-group-info > a")
    for current_profile_link in tmp_profile_links:
        profile_links.append(current_profile_link.get_attribute("href"))
    return profile_links


def login():
    global driver
    driver.get("https://kalibrr.ph/login")
    wait_for_page_load()
    time.sleep(small_wait_time)
    email_input = driver.find_element_by_name("email")
    email_input.clear()
    email_input.send_keys(email)
    password_input = driver.find_element_by_name("password")
    password_input.clear()
    password_input.send_keys(password)
    login_button = driver.find_element_by_class_name("btn-block")
    login_button.send_keys(Keys.RETURN)


def wait_for_page_load():
    current_wait_time = 0
    while 1:
        if page_has_loaded() or current_wait_time == implicit_wait_time:
            break
        time.sleep(1)
        current_wait_time += 1


def page_has_loaded():
    global driver
    page_state = driver.execute_script('return document.readyState;')
    return page_state == 'complete'


if __name__ == "__main__":
    main()



