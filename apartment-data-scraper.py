import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

date_list = []
description_list = []
floor_list = []
age_list = []
room_count_list = []
width_list = []
is_furnished_list = []
natural_gas_list = []
rental_price_list = []

base_url = "/buca-kiralik?page="

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
}
for page_num in range(1, 22): # 1-21 Gezilecek sayfalar.
    url = f'{base_url}{page_num}'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:

        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.find_all('a', href=True, class_='card-link')
        i = 1
        for link in links:
            link_url = link['href']
            if not link_url.startswith('http'):
                link_url = requests.compat.urljoin(url, link_url)

            while True:
                try:
                    link_response = requests.get(link_url, headers=headers)
                    link_response.raise_for_status()
                    break 
                except requests.exceptions.RequestException as e:
                    print("Hata:", e)
                    time.sleep(5)

            if link_response.status_code == 200:
                link_soup = BeautifulSoup(link_response.text, 'html.parser')

                description = link_soup.find('h1', {'class':'fontRB'})
                description_text = description.get_text(strip=True)
                description_list.append(description_text if description_text is not None else "None")

                all_li_elements = link_soup.find_all('li', {'class':'spec-item'})
               
                found_son_guncelleme_tarihi = False
                found_bulundugu_kat = False
                found_bina_yasi = False
                found_oda_sayisi = False
                found_m2 = False
                found_esya = False
                found_yakit = False
                found_kira = False

                for li in all_li_elements:
                    spans = li.find_all('span')
                    if len(spans) >= 2:
                        key_text = spans[0].get_text(strip=True) 
                        value_text = spans[1].get_text(strip=True)
                        if key_text == "Son Güncelleme Tarihi":
                            date_list.append(value_text if value_text is not None else "None")
                            found_son_guncelleme_tarihi = True
                        if key_text == "Bulunduğu Kat":
                            floor_list.append(value_text if value_text is not None else "None")
                            found_bulundugu_kat = True
                        if key_text == "Bina Yaşı":
                            age_list.append(value_text if value_text is not None else "None")
                            found_bina_yasi = True
                        if key_text == "Oda + Salon Sayısı":
                            room_count_list.append(value_text if value_text is not None else "None")
                            found_oda_sayisi = True
                        if key_text == "Brüt / Net M2":
                            width_list.append(value_text if value_text is not None else "None")
                            found_m2 = True
                        if key_text == "Eşya Durumu":
                            is_furnished_list.append(value_text if value_text is not None else "None")
                            found_esya = True
                        if key_text == "Yakıt Tipi":
                            natural_gas_list.append(value_text if value_text is not None else "None")
                            found_yakit = True
                        if key_text == "Kira":
                            rental_price_list.append(value_text if value_text is not None else "None")
                            found_kira = True

                    

            else:
                print(f"Error: {link_response.status_code}")
            print(f"{page_num}. Sayfadaki {i}. ilan tamamlandı.")
            i+=1
            if not found_son_guncelleme_tarihi:
                date_list.append("None")
            if not found_bulundugu_kat:
                floor_list.append("None")
            if not found_bina_yasi:
                age_list.append("None")
            if not found_oda_sayisi:
                room_count_list.append("None")
            if not found_m2:
                width_list.append("None")
            if not found_esya:
                is_furnished_list.append("None")
            if not found_yakit:
                natural_gas_list.append("None")
            if not found_kira:
                rental_price_list.append("None")
            time.sleep(1)

    else:
        print(f"Error: {response.status_code}")
    print(f"{page_num + 1}. sayfaya geçildi.")
    time.sleep(3)

df = pd.DataFrame({
    'Metin': description_list,
    'Tarih': date_list,
    'Kat': floor_list,
    'Yaş': age_list,
    'Oda Sayısı': room_count_list,
    'Genişlik': width_list,
    'Eşyalı mı?': is_furnished_list,
    'Doğalgaz var mı?': natural_gas_list,
    'Kira': rental_price_list,
})
df.to_excel('apartment-data.xlsx', index=False)
