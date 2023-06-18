# **Application integration with an external API.**

# **Table of Contents.**

<ol>
<li><a href="#project-outline">Project Outline</a></li>
<li><a href="#worflow">Workflow</a></li>
<li><a href="#api-response-schemas">API Response Schemas</a></li>
<li><a href="#prerequisites">Prerequisites</a></li>
<li><a href="#important-note-before-you-begin-ssm_flag">Important note before you begin (ssm_flag)</a></li>
<li><a href="#getting-started">Getting Started</a></li>
<li><a href="#running-tests">Running tests</a></li>
<li><a href="#running-the-application-locally">Running the application locally</a></li>
<li><a href="#clean-up">Clean up</a></li>
<li><a href="#troubleshooting">Troubleshooting</a></li>
<li><a href="#potential-improvements">Potential improvements</a></li>
<li><a href="#appendix---directory-structure">Appendix - Directory Structure</a></li>
</ol>

# **Project Outline.**

The aim of this project is to produce a standalone, fault-tolerant application that interacts with an external API.

The application will query different API endpoints for specific data, perform some data manipulation on each API response & send the results back to a different API endpoint.

The application will have run successfully if & only if we receive a 200 OK response from the API endpoint.

# **Workflow.**

The application aims to do the following, in order:

* Initialise the application configuration, including setting parameter secrets.
* Query an external API endpoint at `<app_url>/outages` for relevant outage data - each data point gives information on when the outage started, ended & the battery id identifier associated with the outage.
* Query another external API endpoint at `<app_url>/site-info/<site-id>` for relevant site data - response fields include a site name, id & a list of device data points, each giving information on the device id & name.
* Filter outage data based on two criteria:
    * Remove any outages that occurred on or before January 1st 2022 at 00:00:00.
    * Remove any outage data that isn't relevant to the site with name **"norwich-pear-tree"**.
* "Join" the outages data with the corresponding site-info battery data for the "norwich-pear-tree" site, pulling the battery "name" into the data payload.
* Send (POST) results to the external API endpoint at `<app_url>/site-outages/<site-id>`.

# **API Response Schemas.**

Outlined below, are the JSON schemas we can expect the API response to have when issuing a GET request on the corresponding endpoints:

## **GET `<app_url>/outages`.**

```
[
  {
    "id": string,
    "begin": string,
    "end": string
  },
  {
    "id": string,
    "begin": string,
    "end": string
  },
  .
  .
  .
]
```

## **GET `<app_url>/site-info/<site-id>`.**

```
{
  "id": string,
  "name": string,
  "devices": [
    {
      "id": string,
      "name": string
    },
    {
      "id": string,
      "name": string
    }
    .
    .
    .
  ]
}
```

The API endpoint that we are required to send (POST) the resulting data to, only accepts JSON payloads that are:

* Of the correct schema.
* Contain only the correct data.

All other data sent to the endpoint will receive a 4xx error in response. Below is the expected JSON schema the endpoint expects:

## **POST `<app_url>/site-outages/<site-id>`.**

```
[
  {
    "id": string,
    "name": string,
    "begin": string,
    "end": string
  },
  {
    "id": string,
    "name": string,
    "begin": string,
    "end": string
  },
  .
  .
  .
]
```

# **Prerequisites.**

Application code is written exclusively in Python, in order for our application & tests to run, ensure that any version of Python3 is installed on your local machine.

We can do this using any package manager, such as [Homebrew](https://brew.sh/) - from the root directory of your computer, run the following once Homebrew is installed:

```
brew install python3
```

Installation can be verified using the following command:

```
which python3
```

If successfully installed, you should see the local install location to the python executable.

After we have successfully installed python, we will install a python package called `virtualenv`. This package will allow us to spin up a local, lightweight virtual environment where we can install our project dependencies & run our code.

From the root directory of your computer, run the following:

```
pip3 install virtualenv
```

<br>

**In more cases than not, it is also vital that the `ssm_flag` in `app.py` is set to `False` - more information on that can be found directly below.**

Providing that we are planning to run this application locally & without AWS Parameter Store, user knowledge of API URL & Key values is essential.

# **Important note before you begin (ssm_flag).**

During development of this application, I have followed the well-known principle of **"never ever hard-code your application secrets"**.

Hence, I originally stored all application secrets such as API URL & API Key in a relevant secrets manager during development work. In the case of this project, I decided to use AWS Parameter Store in my personal AWS account.

Typically, when working as part of a team in a professional development environment, most team members should have access to the same AWS (or any cloud provider) account & the secrets / parameters contained within it.

I understand that this isn't possible in the case of this project, so have utilised environment variables to allow the user to set API URL & Key values before running the application & tests locally.

I have however, decided to keep the AWS Parameter Store functionality in place & toggle whether it is used or not [here](https://github.com/dantaylrr/api-app-tt/blob/main/src/main/app.py#L47) using the `ssm_flag` parameter.

Functionality of the `init_config` method with AWS Parameter Store is still achievable by the user should they wish, they simply have to create the parameter names defined in `config.yaml` in their own AWS accounts & have the ability to retrieve these at runtime.

# **Getting Started.**

Firstly, open up the terminal (if on MacOS) or Command Prompt (if on Windows) on your local machine, decide beforehand where you would like to clone this repository & navigate to the root of this directory. 

Once you have navigated to the appropriate directory, begin by cloning the repository locally via. SSH using the repository SSH address.

From your current working directory, run:

```
git clone git@github.com:dantaylrr/api-app-tt.git
```

If cloning via SSH is proving to be problematic, you can attempt to clone the repository via HTTPs (but is generally not advised):

```
git clone https://github.com/dantaylrr/api-app-tt.git
```

Once you have successfully cloned the repository locally, navigate to the root of the project:

```
cd api-app-tt
```

A simple `ls` command from this directory should yield the following:

```
src/
tests/
.gitignore
README.md
config.yaml
setup.py
requirements.txt
```

Now, we want to create a virtual environment to install all of our dependencies, run tests & run our application code. You can create a virtual environment `env` using `virtualenv` installed in <a href="#prerequisites">Prerequisites</a> the following command from the project root:

```
python3 -m venv env
```

We will also have to activate our python virtualenv executable in order to run python code in our virtual environment, do this by running:

```
source env/bin/activate
```

We can verify that our virtual environment has been successfully created by running `pip3 list`, we should **NOT** see all of our global package installs.

Let's finish off getting started by installing our dependencies listed in `requirements.txt` & setting up the project root as a package (for relative imports).

Run the following two commands from the project root:

1). Install `requirements.txt` in our virtual environment:

```
pip3 install -r requirements.txt
```

2). Using `setup.py`, package our application code to be usable:

```
pip3 install .
```

Note - if you want to make changes to code & have changes reflected in any subsequent application runs, install `setup.py` in "developer" mode by specifying the `-e` flag to the above command.

Now that the above commands have finished running - we are almost ready to run some tests & our application locally.

# **Running tests.**

Following on from <a href="#getting-started">Getting Started</a>, you should find yourself in the projects' root directory.

As mentioned in <a href="#important-note-before-you-begin-ssm_flag">Important note before you begin (ssm_flag)</a>, we will need to export some environment variables before any of our API calls are made, as we need to know where to send them & what authorisation password to use!

Before we run our tests, let's define our environment variables, in the project root, run the following commands, replacing the values with the API URL & Key that you know of.

```
export KRAKEN_API_URL=<url>
```
&
```
export KRAKEN_API_KEY=<key>
```

**Note - the Windows / Command Prompt equivalent of `export` is `set`.**

Values can be verified using the `echo` command.

Once environment variables have been verified, we can run the following commands, utilising `pytest`, python's most commonly used testing library.

```
python3 -m pytest -v tests/ -log-cli=true
```

The above command will run both unit & integration tests.

# **Running the application locally.**

This section assumes that the appropriate environment variables have been set, as per section <a href="#running-tests">Running tests</a>.

From the projects' root directory (same place tests were ran), run the following command - this tells python to load our app as a module, instead of a top-level script:

```
python3 -m src.main.app
```

You should see the application output logs in the terminal where you ran the command.

You can verify the success of the application run by inspecting these logs, providing everything has worked as expected, you should see the following log entry (2nd to last):

```
INFO:__main__:Site-info POST request response: Status code = 200.
```

# **Clean up.**

Do not forget to deactivate your virtual environment by running `deactivate` from the root of the project directory.

# **Troubleshooting.**

Any status code outside of a 2xx (200) error you might see here means that the application has failed to post the correct payload to the API endpoint, try starting again from <a href="#prerequisites">Prerequisites</a> before attempting another run.

Any `RuntimeError` that may arise after running the above command means that the application has failed to complete, typically this occurs when our environment variables `KRAKEN_API_URL` or `KRAKEN_API_KEY` either haven't been set correctly, or have been set with the incorrect values.

# **Potential improvements.**

Below is a list of potential improvements I would consider implementing given more time & if this piece of work was to go into a production environment:

* **Verification methods of API responses** - in common production environments, data is constantly changing, being updated, appended to, growing etc. This application only deals with static data, if data was non-static & grew as time progressed, I would definitely look to validate any API responses in the application it self, making it further fault-tolerant.

* **"Generalise" application inputs** - the current application is only concerned about the site-id "norwich-pear-tree". What if we also wanted our application to run for a different site-id? e.g. "kingfisher", we could do this by supplying a list of site-id inputs.

* **Containerisation of application** - this would allow my application to be deployed into any environment in a "lift-and-shift" manner. I have done this prior when deploying python code to a Lambda via Docker.

* **Repository nice-to-haves** - Github actions workflow file to automate tests on PR's, automatically deploy to different environments etc.

# **Appendix - Directory Structure.**

```
📦 api-app-tt
src/
├─ main/
│  ├─ app.py
├─ utils/
│  ├─ api/
│  │  ├─ api.py
│  ├─ config/
│  │  ├─ initialise_config.py
│  ├─ transformation/
│  │  ├─ filter_outages.py
│  │  ├─ generate_result.py
tests/
├─ events/
│  ├─ outages/
│  │  ├─ invalid_outages.json
│  │  ├─ valid_outages.json
│  ├─ output/
│  │  ├─ invalid_output.json
│  │  ├─ valid_output.json
│  ├─ site-info/
│  │  ├─ invalid_site_info.json
│  │  ├─ valid_site_info.json
├─ unit/
│  ├─ test_methods.py
├─ integration/
│  ├─ test_e2e_app.py
.gitignore
README.md
config.yaml
setup.py
requirements.txt
```
