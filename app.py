from flask import Flask
from flask_restful import Resource, Api, reqparse
from bs4 import BeautifulSoup
import requests, time
from selenium import webdriver
from random import randint

app = Flask(__name__)
api = Api(app)

class GetNormalPrice(Resource):
    def __init__(self):
        self.url_to_crawl = ""
        self.items = []
        self.where = ""


    def start_driver(self):
        print("starting drvier")
        self.driver = webdriver.Chrome("/var/chromedriver/chromedriver")
        time.sleep(4)


    def close_driver(self):
        print('closing driver...')
        # self.display.stop()
        self.driver.quit()
        print('closed!')


    def get_page(self, url):
        print('getting page...')
        self.driver.get(url)
        time.sleep(randint(2, 3))


    def grab_items(self):
        print('grabbing items...')
        data = dict()

        if self.where == "shilla":
            data['pd_brand'] = self.driver.find_element_by_class_name("prtit_wrap").find_element_by_class_name("point").text
            print("grab_items func : pd_brand : " + data['pd_brand'])

            data['pd_name'] = self.driver.find_element_by_class_name("pd-name").text
            print("grab_items func : pd_name : " + data['pd_name'])

            data['pd_price'] = self.driver.find_element_by_class_name("pd-sale").text
            print("grab_items func : pd_price : " + data['pd_price'])

            data['pd_img'] = self.driver.find_element_by_class_name("pd-img").get_attribute("src")
            print("grab_items func : pd_img : " + data['pd_img'])

            self.items.append(data)
            print("grab_items func : items : " + self.items.__str__())

        elif self.where == "ssg":
            data['pd_brand'] = self.driver.find_element_by_class_name("foreignTxt").text
            print("grab_items func : pd_brand : " + data['pd_brand'])

            data['pd_name'] = self.driver.find_element_by_class_name("product-name").text
            print("grab_items func : pd_name : " + data['pd_name'])

            data['pd_price'] = self.driver.find_element_by_id("totalAmtWon").text
            print("grab_items func : pd_price : " + data['pd_price'])

            data['pd_img'] = self.driver.find_element_by_id("prdtImageZoom").find_element_by_tag_name("img").get_attribute("src")
            print("grab_items func : pd_img : " + data['pd_img'])

            self.items.append(data)
            print("grab_items func : items : " + self.items.__str__())

        else:
            exit(1)
            print("유효하지 않은 면세점 URL")


    def parse(self):
        self.start_driver()
        self.get_page(self.url_to_crawl)
        self.grab_items()
        self.close_driver()

        if self.items:
            return self.items
        else:
            return False, False


    def post(self):
        # try:
            parser = reqparse.RequestParser()
            parser.add_argument('pd_url', type=str)
            args = parser.parse_args()

            pd_url = args['pd_url']

            if 'shilladfs.com' in pd_url:
                self.where = "shilla"
                self.url_to_crawl = pd_url
                print("url to crawl : " + self.url_to_crawl)

                result = self.parse()

            # 신세계 면세점 수정 필요함..
            elif 'ssgdfm.com' in pd_url:
                self.where = "ssg"
                ori_url, ssg_prdtCode = pd_url.split('=')
                ssg_reurl = 'http://www.ssgdfm.com/shop/product/ajax/getProductItemViewBox?prdtCode=' + ssg_prdtCode

                self.url_to_crawl = ssg_reurl
                print("url to crawl : " + self.url_to_crawl)

                result = self.parse()

            else:
                print("else")

            return {'status' : "success",
                    'data' : result
                    }, 200

        # except Exception as e:
        #     return {'status' : "error",
        #             'data' : str(e)
        #             }

api.add_resource(GetNormalPrice, '/api')

if __name__ == '__main__':
    app.run(debug=True)
