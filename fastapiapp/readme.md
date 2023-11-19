# an app for predicting CL prices

#run app simple
uvicorn main:app --reload

Running locally in docker:
    docker run --rm -p 8080:8080 -e MODE=staging swimleftproducts2/pricesto 

Update req:
    freeze requirements with pipreqs
        pipreqs . --force

Build image 
    docker image build -t swimleftproducts2/pricesto . 

Push image
    docker push swimleftproducts2/pricesto:latest