*** Settings ***
Documentation  Tests for http://vetdoc.co/
...
Library  pubmed.py
Library  pubmed.PubmedHomePage
Library  pubmed.PubmedDocsumPage 
Library  pubmed.PubmedArticlePage

*** Test Cases ***
Open Vetdoc
    Open Vetdoc
    Maximize Window
    All Elements On Page


Whether language can be switched
    Switch Between Langauges


Whether it is possible to switch between Clinic and Veterinarian in the Name search field
    Switch Between Clinics And Veterinarians


Whether delete buttons in the search fields (Address, Name) are working
	Clear Address Field
	Clear Name Field


Whether Address autocomplete works
	${value}=  random_value
	Search By Address  ${value}
    Choose Veterinar
    # Click Result On Pubmed Docsum Page  1
    # Pubmed Article Page Body Should Contain  London
    [Teardown]  Close Pubmed Article Page


