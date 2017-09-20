import bs4 as bs
import urllib.request
import datetime, calendar
from twilio.rest import Client

# Twilio Setup
account_sid = ''
auth_token = ''

client = Client(account_sid, auth_token)
send_to_list = ['']
twilio_number = ''
receive_upcoming_bool = False
#

weekday_name = calendar.day_name[datetime.date.today().weekday()]

events_url = 'https://public.1871.com/events?category_no=1190'
link_base_url = 'https://public.1871.com'

source = urllib.request.urlopen(events_url).read()
soup = bs.BeautifulSoup(source,'lxml')

upcoming_events_table = soup.find_all('ul', 'blocks blocks_equalHeight blocks_3to2to1')

table_elements = []
element_dates = []
element_titles = []
element_bodies = []
element_venues = []
element_links = []

for list_element in upcoming_events_table[0].find_all('li'):
	table_elements.append(list_element)


for element in range(len(table_elements)):
	for date_text in table_elements[element].find_all('span', 'label mix-label_lg mix-label_dark'):
		element_dates.append(date_text.text)
	for title_text in table_elements[element].find_all('a', 'hdg hdg_6 vr-override_x4'):
		element_titles.append(title_text.text)
	for body_text in table_elements[element].find_all('span', 'txt'):
		element_bodies.append(body_text.text)
	for venue_text in table_elements[element].find_all('span', 'txt txt_feature'):
		element_venues.append(venue_text.text)
	for link_text in table_elements[element].find_all('a', 'btn mix-btn_stretch'):
		element_links.append(link_base_url + link_text.get('href'))

element_bodies = element_bodies[0::2]

def check_if_element_today(element_date):
	element_date = element_date[:-11]
	element_date = element_date.replace(' ','')
	element_date = element_date.replace(',','')
	if len(element_date) == 12:
		event_year = element_date[8:12]
		event_month_abv = element_date[3:6]
		event_month = convert_abv_to_int(event_month_abv)
		event_day = element_date[6:8]
	elif len(element_date) == 11:
		event_year = element_date[7:11]
		event_month_abv = element_date[3:6]
		event_month = convert_abv_to_int(event_month_abv)
		event_day = element_date[6]
		event_day = convert_single_digit_days(event_day)
	datetime_comparator = event_year+'-'+event_month+'-'+event_day
	datetime_today = str(datetime.date.today())
	if datetime_comparator == datetime_today:
		return True
	else:
		return False

def check_if_element_soon(element_date):
	element_date = element_date[:-11]
	element_date = element_date.replace(' ','')
	element_date = element_date.replace(',','')
	if len(element_date) == 12:
		event_year = element_date[8:12]
		event_month_abv = element_date[3:6]
		event_month = convert_abv_to_int(event_month_abv)
		event_day = element_date[6:8]
	if len(element_date) == 11:
		event_year = element_date[7:11]
		event_month_abv = element_date[3:6]
		event_month = convert_abv_to_int(event_month_abv)
		event_day = element_date[6]
		event_day = convert_single_digit_days(event_day)
	datetime_comparator = event_year+'-'+event_month+'-'+event_day
	days_considered_soon = 2
	days_possible = []
	for i in range(1,days_considered_soon+1):	
		days_possible.append(str(datetime.date.today() + datetime.timedelta(days=i)))
	if datetime_comparator in days_possible:
		return True
	else:
		return False

def convert_abv_to_int(event_month_abv):
	if event_month_abv == 'Jan':
		return '01'
	elif event_month_abv == 'Feb':
		return '02'
	elif event_month_abv == 'Mar':
		return '03'
	elif event_month_abv == 'Apr':
		return '04'
	elif event_month_abv == 'May':
		return '05'
	elif event_month_abv == 'Jun':
		return '06'
	elif event_month_abv == 'Jul':
		return '07'
	elif event_month_abv == 'Aug':
		return '08'
	elif event_month_abv == 'Sep':
		return '09'
	elif event_month_abv == 'Oct':
		return '10'
	elif event_month_abv == 'Nov':
		return '11'
	elif event_month_abv == 'Dec':
		return '12'
def convert_single_digit_days(event_day):
	if event_day == '1':
		return '01'
	elif event_day == '2':
		return '02'
	elif event_day== '3':
		return '03'
	elif event_day == '4':
		return '04'
	elif event_day== '5':
		return '05'
	elif event_day == '6':
		return '06'
	elif event_day == '7':
		return '07'
	elif event_day == '8':
		return '08'
	elif event_day == '9':
		return '09'

if_today_bools = []
if_soon_bools = []

for element_date in element_dates:
	if_today_bools.append(check_if_element_today(element_date))

for element_date in element_dates:
	if_soon_bools.append(check_if_element_soon(element_date))

# print(if_today_bools)
# print(if_soon_bools)

def twilio_today(index):
	formatted_time = element_dates[index][-8:]
	formatted_time = formatted_time.replace(' ','')
	formatted_time = formatted_time[0:4]+' '+formatted_time[-2:]
	txt_content = 'Event Today @ '+formatted_time+'\n'+element_titles[index]+'\n\U0001F4CD'+element_venues[index]+'\n'+element_links[index]
	return (txt_content)

def twilio_events_soon(index):
	formatted_time = element_dates[index][0:9]+' @ '+element_dates[index][-7:]
	# formatted_time = formatted_time.upper()
	txt_content = 'Upcoming Event- '+formatted_time+'\n'+element_titles[index]+'\n\U0001F4CD'+element_venues[index]+'\n'+element_links[index]
	return (txt_content)

def twilio_determine_content_events_soon():
	for index in range(len(if_soon_bools)):
		if if_soon_bools[index]:
			txt_content = twilio_events_soon(index)
			messages_to_send.append(txt_content)

def twilio_determine_content_daily():
	for index in range(len(if_today_bools)):
		if if_today_bools[index]:
			txt_content = twilio_today(index)
			messages_to_send.append(txt_content)	

messages_to_send = []
if receive_upcoming_bool == True:
	twilio_determine_content_daily()
	twilio_determine_content_events_soon()
else: 
	twilio_determine_content_daily()

if len(messages_to_send) != 0:
	for message in messages_to_send:
		for number in send_to_list:
			client.messages.create(
				to=number, from_=twilio_number, body=message
			)	



                      
                                 
