import scrapy
import json
import psycopg2

headers = {
    "Host": "www.sreality.cz",
    "User-Agent": "Googlebot",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "sl,en-GB;q=0.7,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.sreality.cz/hledani/prodej/byty",
    "Cookie": 'qusnyQusny=1; lps=eyJfZnJlc2giOmZhbHNlLCJfcGVybWFuZW50Ijp0cnVlfQ.ZZe9cw.Ry5CpL9ApttpvrhW2DFkmK63JVA; cmpredirectinterval=1704965932006; sid=id=8815977881490896057|t=1704361139.114|te=1704443253.170|c=00794AFE8B9293802A0DC95CAD790ACA; .seznam.cz|sid=id=8815977881490896057|t=1704361139.114|te=1704443253.170|c=00794AFE8B9293802A0DC95CAD790ACA; sid=id=8815977881490896057|t=1704361139.114|te=1704443253.170|c=00794AFE8B9293802A0DC95CAD790ACA; euconsent-v2=CP325IAP325IAD3ACBCSAhEsAP_gAEPgAATIJVwQQAAwAKAAsACAAFQALgAZAA6ACAAFAAKgAWgAyABoADmAIgAigBHACSAEwAJwAVQAtgBfgDCAMUAgACEgEQARQAjoBOAE6AL4AaQA4gB3ADxAH6AQgAkwBOACegFIAKyAWYAuoBgQDTgG0APkAjUBHQCaQE2gJ0AVIAtQBbgC8wGMgMkAZcA0oBqYDugHfgQHAhcBGYCVYIXQIoAFAAWABUAC4AIAAZAA0ACIAEcAJgAVQAtgBiAD8AISARABEgCOAE4AMsAZoA7gB-gEIAIsAXUA2gCbQFSALUAW4AvMBggDJAGpgQuAAAAA.YAAAAAAAAAAA; szncmpone=1; seznam.cz|szncmpone=1; szncsr=1704443248; __gfp_64b=ZNfB.CSSPqJbdfKnQOFfQ9vfuEqySMUPoi6o7ZwOQXH.p7|1704361139; udid=NGs8ULKRjGXF4deV-ZODM_6q8AAdF4nR@1704361139021@1704361139021; lastsrch="{\"category_main_cb\": \"1\"\054 \"per_page\": \"60\"\054 \"tms\": \"1704443252992\"\054 \"category_type_cb\": \"1\"}"; per_page=60; __cc=amNSM1BTV1JtZ21LaUJvZTsxNzA0NDUzNzk5:NHFZYndMdnBEU0RtV3Y0cjsxNzA0NDY4MTk5; last-redirect=1; cmprefreshcount=0|2fuek1dnae',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "TE": "trailers"
}




class SrealitySpider(scrapy.Spider):
    name = "sreality"
    allowed_domains = ["www.sreality.cz"]
    start_urls = ["https://www.sreality.cz/api/cs/v2/estates?category_main_cb=1&category_type_cb=1&per_page=500&tms=1704443257846"]


    def start_requests(self):
        pagination_url =f"https://www.sreality.cz/api/cs/v2/estates?category_main_cb=1&category_type_cb=1&per_page=500&tms=1704443257846"
        yield scrapy.Request(url=pagination_url,headers=headers, callback=self.parse_pages)
       

    def parse_pages(self,response) :
        try:
            data = json.loads(response.body)
            estates = data["_embedded"]["estates"]
            flats_json = []
            for i,estate in enumerate(estates) :
                flats_json_ = {}
                labels = ", ".join([label for label in estate["labels"]])
                
                image_links = [ link["href"] for link in estate["_links"]["images"]][0] # ONLY USE THE FIRST IMG
                flats_json_["name"] = estate["name"]
                flats_json_["price"] = str(estate["price"]) + " (CZK)"
                flats_json_["locality"] = estate["locality"] 
                flats_json_["label"] = labels
                flats_json_["image_url"] = image_links
                flats_json.append(flats_json_)
            
        except json.JSONDecodeError as e:
            self.logger.error(f'JSON parsing error in parse_data_page: {e}')

        conn = psycopg2.connect(
            dbname="mydatabase",
            user="myuser",
            password="mypassword",
            host="postgres",
            port="5432",
            options='-c client_encoding=utf-8'     
        )

        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE flats (
                name VARCHAR,
                price VARCHAR,
                locality VARCHAR,
                image_url VARCHAR
            );
        """)
        for  flat in flats_json:
            
            cur.execute("""
                INSERT INTO flats (name, price, locality, image_url)
                VALUES (%s, %s, %s, %s)
            """, (flat['name'], flat['price'], flat['locality'], flat['image_url']))

        conn.commit()
        cur.close()
        conn.close()
        