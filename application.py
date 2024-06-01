from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging

# Setting up logger
logging.basicConfig(filename="scrapper.log", level=logging.DEBUG, format="%(asctime)s | %(levelname)s | %(message)s")

application = Flask(__name__)
app = application

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div",{"class":"cPHDOP col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a["href"]
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            print(prod_html)
            commentboxes = prod_html.find_all("div",{"class":"col EPCmJX"})

            filename = searchString + ".csv"
            fw = open(filename, "a")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.find_all("p",{"class":"_2NsDsF AwS1CA"})[0].text

                except Exception as e:
                    logging.error(f"No name found! Error: {e}")

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.text


                except Exception as e:
                    logging.error(f"No rating found! Error: {e}")

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.p.text

                except Exception as e:
                    logging.warning(f"No commentHead found! Error: {e}")
                try:
                    comtag = commentbox.findAll("div",{"class":""})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].text
                except Exception as e:
                    logging.warning(f"No comments found! Error: {e}")

                fw.write(f"{searchString}, {name}, {rating}, {commentHead}, {custComment}\n")

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            logging.info("log my final result {}".format(reviews))
            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.exception(f"Oops you got an error: {e}")
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")
