from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from timeit import default_timer as timer

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

CHANNELS_PAGE = "https://twitchtracker.com/channels/ranking?page="
NAME_PAGE = "https://twitchtracker.com/"

'''
DATASET COLUMNS
NAME, RANK, LANGUAGE, TYPE, MOST_STREAMED_GAME, 2ND_MOST_STREAMED_GAME
AVERAGE_STREAM_DURATION, FOLLOWERS_GAINED_PER_STREAM, AVG_VIEWERS_PER_STREAM, AVG_GAMES_PER_STREAM
TOTAL_TIME_STREAMED, TOTAL_FOLLOWERS, TOTAL_VIEWS, TOTAL_GAMES_STREAMED
ACTIVE_DAYS_PER_WEEK, MOST_ACTIVE_DAY, DAY_WITH_MOST_FOLLOWERS_GAINED
'''

'''
If you wanted to get more esports pages, just use get_name_and_rank on the webpage "https://twitchtracker.com/channels/ranking/esports/page="
I only needed the most popular esports pages out of the most popular 1000 streamers, so to avoid an unnecesarry request, I wrote them all here
'''
# NEEDED FOR get_streamer_type function
ESPORTS_PAGES = ['riotgames', 'playapex', 'lolpacifictw', 'pgl_dota2', 'gaules', 'ow_esports', 'eslcs', 'brawlstars', 'rocketleague',
'otplol_', 'valorant_americas', 'valorant_jpn', 'easportsfc', 'rainbow6', 'esports_rage', 'esl_dota2', 'warcraft', 'valorant_emea',
'eslcsb', 'riotgamesjp', 'valorant', 'magic', 'fortnite', 'worldoftanks', 'evo', 'nba2kleague', 'esl_dota2ember', 'twitchrivals', 'pgl_dota2en2',
'aussieantics', 'brawlhalla', 'cct_cs', 'esl_dota2storm', 'valorant_br', 'chess', 'lla', 'laligafcpro', 'luminositygaming', 'rocketbaguette',
'valorant_fr', 'tekken', 'rainbow6bravo', 'eamaddennfl', 'lvpes', 'cblol', 'pubg_battlegrounds', 'valorant_la', 'imls', 'alphacast', 
'worldofwarships', 'vgbootcamp', 'rainbow6br', 'solaryhs', 'formula1', 'ligue1ubereats', 'solary', 'echo_esports', 'eslcsc']
def normalize_number(num: str):
    multiplier = 1
    num = num.replace(",", ".")
    if num[-1]=="M": multiplier=10**6
    elif num[-1]=="K": multiplier=1000
    num = num.removesuffix("M").removesuffix("K")
    return int(float(num)*multiplier)

# columns 1 and 2 (id and num)
def get_name_and_rank(page: int):
    url = CHANNELS_PAGE + str(page)
    driver.get(url)
    rows = driver.find_elements(By.TAG_NAME, "tr")
    l = []
    for ind, row in enumerate(rows):
        columns = row.find_elements(By.TAG_NAME, "td")
        if (len(columns) == 11):
            # if streamer name has non-latin characters we have to use the url from the name and not the name column
            name = columns[2].find_element(By.TAG_NAME, "a").get_attribute("href").rsplit("/")[-1]
            rank = columns[0].text
            l.append((rank, name))
    return l
# column 3 (category)
def get_language_from_streamer(name: str):
    url = NAME_PAGE + name
    driver.get(url)
    streamer_info = driver.find_element(By.CLASS_NAME, "list-group")
    li_tags = streamer_info.find_elements(By.TAG_NAME, "li")
    language_list_item = li_tags[4]
    language = language_list_item.find_element(By.TAG_NAME, "a").get_attribute("href").rsplit("/")[-1]
    return language
# column 4 (category)
def get_streamer_type(name: str):
    return "esports" if name in ESPORTS_PAGES else "personality"
# column 5 and 6 (category)
def get_2_most_streamed_game(name: str):
    url = NAME_PAGE + name
    driver.get(url)
    try:
        main_div = driver.find_element(By.ID, "channel-games")
        game_links = main_div.find_elements(By.TAG_NAME, "a") # 6 links in total, we need first 2
        first_game = game_links[0].find_element(By.TAG_NAME, "div").get_attribute("data-original-title")
        try:
            second_game = game_links[1].find_element(By.TAG_NAME, "div").get_attribute("data-original-title")
        except:
            return [first_game, '']
        return [first_game, second_game]
    except:
        return ['', '']
# column 7 (num)
def get_avg_stream_duration(name: str):
    url = NAME_PAGE + name
    driver.get(url)
    main_div = driver.find_element(By.CLASS_NAME, "col-sm-6")
    main_table = main_div.find_elements(By.TAG_NAME, "tr") # should be 4 rows
    columns = main_table[2].find_elements(By.TAG_NAME, "td") # 2 td's
    time = columns[1].text # in format "x hrs"
    time = time.split()[0]

    return time
# column 8 (num)
def get_avg_followers_gained_per_stream(name: str):
    url = NAME_PAGE + name
    driver.get(url)
    main_div = driver.find_element(By.CLASS_NAME, "col-sm-6")
    main_table = main_div.find_elements(By.TAG_NAME, "tr") # should be 4 rows
    columns = main_table[1].find_elements(By.TAG_NAME, "td") # 2 td's
    followers = columns[1].text
    return followers.replace(",",".")
# column 9 (num)
def get_avg_views_per_stream(name: str):
    url = NAME_PAGE + name + "/statistics"
    driver.get(url)
    main_section = driver.find_element(By.ID, "report")
    divs = main_section.find_elements(By.TAG_NAME, "div") # 5 divs in total, we need the 4th
    table_rows = divs[3].find_elements(By.TAG_NAME, "tr") # 3 in total, we need the 2nd
    columns = table_rows[1].find_elements(By.TAG_NAME, "td") # 3 in total, we need the 2nd
    views = columns[1].text.split("/")[0].rstrip()
    return views.replace(",",".")
# column 10 (num)
def get_avg_games_per_stream(name: str):
    url = NAME_PAGE + name
    driver.get(url)
    main_div = driver.find_element(By.CLASS_NAME, "col-sm-6")
    main_table = main_div.find_elements(By.TAG_NAME, "tr") # should be 4 rows, we need 1st
    columns = main_table[0].find_elements(By.TAG_NAME, "td") # 2 td's
    avg_games = columns[1].text
    return avg_games
# column 11 (num)
def get_total_time_streamed(name: str):
    url = NAME_PAGE + name + "/statistics"
    driver.get(url)
    divs = driver.find_elements(By.CLASS_NAME, "pge-content") # we need the 2nd one
    hours = divs[1].find_element(By.CLASS_NAME, "pge-v").text
    return hours.replace(",",".")
# column 12 (num)
def get_total_followers(name: str):
    url = NAME_PAGE + name + "/statistics"
    driver.get(url)
    divs = driver.find_elements(By.CLASS_NAME, "pge-content") # we need the 1st one
    followers = divs[0].find_element(By.CLASS_NAME, "pge-v").text
    return normalize_number(followers)
# column 13 (num)
def get_total_views(name: str):
    url = NAME_PAGE + name + "/statistics"
    driver.get(url)
    divs = driver.find_elements(By.CLASS_NAME, "pge-content") # we need the 6th one
    views = divs[5].find_element(By.CLASS_NAME, "pge-v").text
    return normalize_number(views)
# column 14 (num)
def get_total_games_streamed(name: str):
    url = NAME_PAGE + name + "/statistics"
    driver.get(url)
    main_section = driver.find_element(By.ID, "report")
    divs = main_section.find_elements(By.TAG_NAME, "div") # 5 divs in total, we need the 2nd
    table_rows = divs[1].find_elements(By.TAG_NAME, "tr") # 3 in total, we need the 3rd
    columns = table_rows[2].find_elements(By.TAG_NAME, "td") # 2 in total, we need the 2nd
    total_games = columns[1].text
    return total_games
#column 15 (num)
def get_active_days_per_week(name: str):
    url = NAME_PAGE + name + "/statistics"
    driver.get(url)
    main_section = driver.find_element(By.ID, "report")
    divs = main_section.find_elements(By.TAG_NAME, "div") # 5 divs in total, we need the 3rd
    table_rows = divs[2].find_elements(By.TAG_NAME, "tr") # 3 in total, we need the 3rd
    columns = table_rows[2].find_elements(By.TAG_NAME, "td") # 2 in total, we need the 2nd
    days = columns[1].text.split(" ")[0]
    return days
# column 16 (category)
def get_most_active_day(name: str):
    url = NAME_PAGE + name + "/statistics"
    driver.get(url)
    main_div = driver.find_element(By.ID, "chart-week-1")
    main_section = main_div.find_element(By.CLASS_NAME, "highcharts-data-labels")
    days = main_section.find_elements(By.TAG_NAME, "tspan")
    l = []
    for day in days:
        if (day.text != ""):
            l.append(int(day.text))
    return "Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split()[l.index(max(l))]
# column 17 (category)
def get_day_with_most_followers_gained(name: str):
    url = NAME_PAGE + name + "/statistics"
    driver.get(url)
    main_div = driver.find_element(By.ID, "chart-week-4")
    main_section = main_div.find_element(By.CLASS_NAME, "highcharts-data-labels")
    days = main_section.find_elements(By.TAG_NAME, "tspan")
    l = []
    for day in days:
        if (day.text != ""):
            l.append(int(day.text.replace(" ","")))
    return "Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split()[l.index(max(l))]

'''
the given functions when called for all the streamers will eventually produce a "too many requests" error, unless we put too much time-off with sleep
in between every function call, but that will take up too much time. Therefore, we need to refactor the calls, since we only access 2 different pages, 
we can cut down the requests from 14 to just 2 per streamer, but that will require some column mixing, so let's be careful
'''

def get_info_from_name_page(name: str):
    '''
    3 5 6 7 8 10
    from the name page we get the following columns (and their order):
    LANGUAGE (3), 2_MOST_STREAMED_GAMES (5 AND 6), AVG_STREAM_DURATION(7), AVG_FOL_PER_STREAM (8), AVG_GAMES_PER_STREAM (10),
    since we used a lot of the same names for variables we will be using scope technique to avoid renaming them all, this will
    be achieved with the if True: statements
    '''
    url = NAME_PAGE + name
    driver.get(url)
    info = []
    # LANGUAGE
    if True: 
        streamer_info = driver.find_element(By.CLASS_NAME, "list-group")
        li_tags = streamer_info.find_elements(By.TAG_NAME, "li")
        language_list_item = li_tags[4]
        language = language_list_item.find_element(By.TAG_NAME, "a").get_attribute("href").rsplit("/")[-1]
        info.append(language)
    # 2_MOST_STREAMED_GAMES
    if True: 
        try:
            main_div = driver.find_element(By.ID, "channel-games")
            game_links = main_div.find_elements(By.TAG_NAME, "a") # 6 links in total, we need first 2
            first_game = game_links[0].find_element(By.TAG_NAME, "div").get_attribute("data-original-title")
            try:
                second_game = game_links[1].find_element(By.TAG_NAME, "div").get_attribute("data-original-title")
            except:
                info.append([first_game, ''])
            info.append([first_game, second_game])
        except:
            info.append(['', ''])
    # AVG_STREAM_DURATION
    if True:
        main_div = driver.find_element(By.CLASS_NAME, "col-sm-6")
        main_table = main_div.find_elements(By.TAG_NAME, "tr") # should be 4 rows
        columns = main_table[2].find_elements(By.TAG_NAME, "td") # 2 td's
        time = columns[1].text # in format "x hrs"
        time = time.split()[0]
        info.append(time)
    # AVG_FOL_PER_STREAM
    if True:
        main_div = driver.find_element(By.CLASS_NAME, "col-sm-6")
        main_table = main_div.find_elements(By.TAG_NAME, "tr") # should be 4 rows
        columns = main_table[1].find_elements(By.TAG_NAME, "td") # 2 td's
        followers = columns[1].text
        info.append(followers.replace(",","."))
    # AVG_GAMES_PER_STREAM
    if True:
        main_div = driver.find_element(By.CLASS_NAME, "col-sm-6")
        main_table = main_div.find_elements(By.TAG_NAME, "tr") # should be 4 rows, we need 1st
        columns = main_table[0].find_elements(By.TAG_NAME, "td") # 2 td's
        avg_games = columns[1].text
        info.append(avg_games)

    return info
        
def get_info_from_statistics_page(name: str):
    '''
    9 11 12 13 14 15 16 17
    from the name page we get the following columns (and their order):
    avg_views_per_stream (9), total_time_streamed (11), total_followers(12), total_views (13), total_games_streamed (14),
    active_days_per_week(15), most_active_day (16), day_with_most_followers_gained (17),
    since we used a lot of the same names for variables we will be using scope technique to avoid renaming them all, this will
    be achieved with the if True: statements
    '''
    url = NAME_PAGE + name + "/statistics"
    driver.get(url)
    info = []
    # avg_views_per_stream
    if True:
        main_section = driver.find_element(By.ID, "report")
        divs = main_section.find_elements(By.TAG_NAME, "div") # 5 divs in total, we need the 4th
        table_rows = divs[3].find_elements(By.TAG_NAME, "tr") # 3 in total, we need the 2nd
        columns = table_rows[1].find_elements(By.TAG_NAME, "td") # 3 in total, we need the 2nd
        views = columns[1].text.split("/")[0].rstrip()
        info.append(views.replace(",","."))
    # total_time_streamed
    if True:
        divs = driver.find_elements(By.CLASS_NAME, "pge-content") # we need the 2nd one
        hours = divs[1].find_element(By.CLASS_NAME, "pge-v").text
        info.append(hours.replace(",","."))
    # get_total_followers
    if True:
        divs = driver.find_elements(By.CLASS_NAME, "pge-content") # we need the 1st one
        followers = divs[0].find_element(By.CLASS_NAME, "pge-v").text
        info.append(normalize_number(followers))
    # get_total_views
    if True:
        divs = driver.find_elements(By.CLASS_NAME, "pge-content") # we need the 6th one
        views = divs[5].find_element(By.CLASS_NAME, "pge-v").text
        info.append(normalize_number(views))
    # get_total_games_streamed
    if True:
        main_section = driver.find_element(By.ID, "report")
        divs = main_section.find_elements(By.TAG_NAME, "div") # 5 divs in total, we need the 2nd
        table_rows = divs[1].find_elements(By.TAG_NAME, "tr") # 3 in total, we need the 3rd
        columns = table_rows[2].find_elements(By.TAG_NAME, "td") # 2 in total, we need the 2nd
        total_games = columns[1].text
        info.append(total_games)
    # get_active_days_per_week
    if True:
        main_section = driver.find_element(By.ID, "report")
        divs = main_section.find_elements(By.TAG_NAME, "div") # 5 divs in total, we need the 3rd
        table_rows = divs[2].find_elements(By.TAG_NAME, "tr") # 3 in total, we need the 3rd
        columns = table_rows[2].find_elements(By.TAG_NAME, "td") # 2 in total, we need the 2nd
        days = columns[1].text.split(" ")[0]
        info.append(days)
    # get_most_active_day
    if True:
        main_div = driver.find_element(By.ID, "chart-week-1")
        main_section = main_div.find_element(By.CLASS_NAME, "highcharts-data-labels")
        days = main_section.find_elements(By.TAG_NAME, "tspan")
        l = []
        for day in days:
            if (day.text != ""):
                l.append(int(day.text))
        info.append("Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split()[l.index(max(l))])
    # get_day_with_most_followers_gained
    if True:
        main_div = driver.find_element(By.ID, "chart-week-4")
        main_section = main_div.find_element(By.CLASS_NAME, "highcharts-data-labels")
        days = main_section.find_elements(By.TAG_NAME, "tspan")
        l = []
        for day in days:
            if (day.text != ""):
                l.append(int(day.text.replace(" ","")))
        info.append("Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split()[l.index(max(l))])

    return info

FUNCTIONS = [get_language_from_streamer, get_streamer_type, get_2_most_streamed_game, get_avg_stream_duration, get_avg_followers_gained_per_stream,
            get_avg_views_per_stream, get_avg_games_per_stream, get_total_time_streamed, get_total_followers, get_total_views, get_total_games_streamed, 
            get_active_days_per_week, get_most_active_day, get_day_with_most_followers_gained ]

def ready_data(data):
    if (type(data)==list): return f"{str(data[0])},{str(data[1])}"
    else: return str(data)

# this is for creating the dataset.csv file in it's entirety
with open("streamer_names.txt", "r", encoding="utf-8") as read_file, open("dataset.csv", "a") as write_file:
    for ind, streamer in enumerate(read_file, 1):
        rank, name = streamer.split(",")
        rank = rank[1:] # to get rid of the # in front
        print(rank, name.rstrip())
        write_file.write(f'{rank},{name.rstrip()},')
        try:
            info1 = get_info_from_name_page(name)
            sleep(3) # precautionary sleep
            info2 = get_info_from_statistics_page(name)
            # name 3 5 6 7 8 10
            # stats 9 11 12 13 14 15 16 17
            write_file.write(info1[0]+",") # 3
            write_file.write(get_streamer_type(name)+",") # 4
            for i in info1[1:-1]: # 5-8
                write_file.write(ready_data(i)+",") 
            write_file.write(info2[0]+",") # 9
            write_file.write(info1[-1]+",") # 10
            for i in info2[1:]: # 11-17
                write_file.write(ready_data(i))
                if i!=info2[-1]: write_file.write(",")
        except:
            pass
        write_file.write("\n")

# this code snippet can be used to get all columns for a single streamer
'''for fun in FUNCTIONS:
        data = fun("etoiles")
        if (type(data)==list): print(f"{str(data[0])},{str(data[1])}", end="")
        else: print(str(data), end="")
        if fun==FUNCTIONS[-1]: print(",")'''
