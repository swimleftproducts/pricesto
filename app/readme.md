This is a flask app that runs on digital ocean

Running locally:
    export FLASK_APP=run.py
    export MODE=local
    export DATABASE_URI= in .env
    export SECRET= in .env
    
    run with python app.py


Running locally in docker:
    docker run --rm -p 8080:8080 -e MODE=staging swimleftproducts2/pricesto

Update req:
    freeze requirements with pipreqs
        pipreqs . --force

Build image 
    docker image build -t swimleftproducts2/pricesto . 

Push image
    docker push swimleftproducts2/pricesto:latest