# Beyond Chaos Flask App
When running, this Flask app will allow you to upload a Final Fantasy 3/6 .smc or .sfc file, and will then produce a Beyond Chaos modification of a ROM file, with an option to download the .smc and .txt log.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

Python 3.7 or higher

### Installing

This project can be installed locally for testing purposes. In order to do that, first, navigate to the directory you'd like to install in, then:

```
git clone git@github.com:razzlestorm/BCRandomizer-API.git
```

then, navigate into that folder and type:

```
pip install -r requirements.txt
```

You will also need to create a .env file with the following environment variables:
QUART_SECRET_KEY,
ALLOWED_EXTENSIONS,
UPLOAD_FOLDER.

For more about .env files, please visit see the [dotenv project](https://pypi.org/project/python-dotenv/).

Finally, to run the project locally:

```
python quart_app/app.py
```

## TO DO

* Separate functions/routes
* Get async functionality working
* Check for conflicting modes/flags
* Create better checks for improper smc files.
* Create graphics for the html files
* Enable batch generation of files.


## Deployment
This project is currently deployed to a free Heroku node, [here](https://bcrandomizerapi.herokuapp.com/)

## Built With
* [Quart](https://pgjones.gitlab.io/quart/) - The web framework used

## Contributing
Please fork and feel free to reach out to me on Discord with any questions! 

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **abyssonym** - *Initial work* - [Abyssonym](https://github.com/abyssonym/beyondchaos)
* **SubtractionSoup** - *Contributor* - [SubtractionSoup](https://github.com/subtractionsoup/beyondchaos)
* **Razzle Storm** - *API Contributor* - [Razzle Storm](https://github.com/razzlestorm/BCRandomizer-API)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc