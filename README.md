# Catalog App

A simple app containing posts and their respective categories.

## Getting Started

### Prerequisites

This app is designed to run on the Vagrant VM: https://github.com/udacity/fullstack-nanodegree-vm 
Clone this repo into the desired folder and once inside the vagrant folder run:

```
vagrant up
```

After the virtual machine has finished loading log into it with ssh:

```
vagrant ssh
```

Once logged go into the vagrant shared folder with

```
cd /vagrant
```

### Dependencies

To install all dependencies run:
```
pip install -r requirements.txt
```

### Database Setup

And proceed to navigate to the catalog folder and then run the db_setup by entering the following command:

```
python db_setup.py
```

After the script has finished creating the database you should have a file called catalogdb.db which is the database containing all the tables of the app.

If you wish to populate the database with fake data for testing purposes you can run the python script "dummydata.py" with 

```
python dummydata.py
```

### Running the app

After everything is set-up the local server and app can be started by running

```
python catalog_project.py
```

You can now use the app by going to localhost:5000

## API Endpoints

For a list of all the current items in the app
```
/catalog/api/items
```

A list of current categories in the app
```
/catalog/api/categories
```

The list of items in a specific category according to it's id
```
/catalog/api/category/(ID of specific category)/items
```

For a specific Item the url would be
```
/catalog/api/item/(ID of specific item)/
```