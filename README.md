# BibliQAl - QA engine on bible commentaries  
Bibliqal takes in natural language questions and outputs relevant answers from famous "legit" docummentaries.  

<img src = "img/Bibliqal - Jews and the gospel.gif">  

## Usage by Docker
1. You can either pull my docker image: `sudo docker pull vinitrinh/bibliqal`  
Or create a new one `sudo docker build -t bibliqal .`  
2. Run a container: `sudo docker run -p 5000:5000 bibliqal`  
## Usage locally

1. Clone Repo
2. Replace data folder with the compressed data folder from: https://drive.google.com/open?id=1Y6DeuYcr3EbzfiDE1hNQDlowyICdrmS0
3. Download the packages.   
`conda create -n bibliqal`  
`pip install -r requirements.txt`
4. Run the streamlit app: `streamlit run app.py` and viola!


## Knowledge Bases
Knowledge bases are taken from the following:
__Bible hub__:  
    - [Expositor's commentary](https://biblehub.com/commentaries/expositors/genesis/1.htm)  
__Blue letter bible__:  
    - [John Macarthur](https://www.blueletterbible.org/commentaries/macarthur_john/)  
    - [Edersheim Alfred](https://www.blueletterbible.org/commentaries/edersheim_alfred/)  
    - [Headley PC](https://www.blueletterbible.org/commentaries/headley_pc/)  
    - [Hocking David](https://www.blueletterbible.org/commentaries/hocking_david/)  
    - [Ice Thomas](https://www.blueletterbible.org/commentaries/ice_thomas/)  
    - [Lightfoot JB](https://www.blueletterbible.org/commentaries/lightfoot_jb/)

Other potential sources for the future:  
1. https://www.tms.edu/m/tmsj15g.pdf  
2. https://www.studylight.org/commentaries/cbb.html  (Brian Bell's commentaries look straightforward)
3. https://www.preceptaustin.org/tool_commentary
4. https://www.bestcommentaries.com/series/free-bible-commentary-fbc/


## Repo Structure
<img src="img/Bibliqal Architecture Diagram.jpeg">  


## Notes
__Note 23 Jan__
1. streamlit is unable to run over a tunnel. This means that the app cannot be served. Till then, we can only wait for the fix.   
2. docker can be used for the app, this will speed up the setup

__Note 21 May__
1. Streamlit supposedly fixed the bug in the latest version 0.56.0.
2. Docker image up on `vinitrinh/bibliqal`