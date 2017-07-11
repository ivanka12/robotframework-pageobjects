from robotpageobjects import Page, robot_alias
from robot.utils import asserts
from time import sleep
from random import randint
from random import choice
from selenium import webdriver


class PubmedHomePage(Page):
    """ Models the Pubmed home page at:
        HOST://ncbi.nlm.nih.gov/pubmed"""


    # Allows us to call this page
    # something other than the default "Pubmed Home Page"
    # at the end of keywords.
    name = "VetDoc"

    # This page is found at baseurl + "/pubmed"
    uri = ""

    # inheritable dictionary mapping human-readable names
    # to Selenium2Library locators. You can then pass in the
    # keys to Selenium2Library actions instead of the locator
    # strings.
    selectors = {
        "search address": "id=id_all",
        "search name": "id=id_name",
        "search button": "id=id_submit",
        "fr button": "id=fr-lang-button",
        "en button": "id=en-lang-button",
        "remove location": "xpath=(//div[@class='remove-loc']/i[@class='fa fa-times'])",
        "remove name": "xpath=(.//div[@class='remove-name']/i[@class='fa fa-times'])",
        # "autocomplete_address": "xpath=/html/body/div[2]",
        "switch button": "xpath=(.//*[@id='react-select-2--value-item'])",
        "choose clinic": "xpath=(.//*[@id='react-select-2--option-1'])",
        "choose veterinars": "xpath=(.//*[@id='react-select-2--option-0'])",
        "veterinar": "xpath=(//*[@id='el-0']/div/div[2]/div/a)",
    }

    # Use robot_alias and the "__name__" token to customize
    # where to insert the optional page object name
    # when calling this keyword. Without the "__name__"
    # token this method would map to either "Type In Search Box",
    # or "Type In Search Box Pubmed". Using "__name__" we can call
    # "Type in Pubmed Search Box  foo".
    @robot_alias("maximize_window")
    def maximize_browser_window(self):
        self._current_browser().maximize_window()
        return self

    def random_value(self):
        return choice(["Par", "Lon", "Kan", "Tem", "Pen", "Del", "Har", "Rec", "Cap", "For"])

    def type_in_search_box(self, txt, search_box, autocomplete):
        for i in range(len(txt)):
           self.input_text(search_box, txt[0:i+1])
           sleep(2)
        self.click_button(search_box)
        autocomplete_text= self.get_text(autocomplete).lower().splitlines()
        sleep(4)
        for element in autocomplete_text:
            asserts.assert_true(txt.lower() in element, "autocomplete_text text does not contain %s" %txt)
        index= randint(1,len(autocomplete_text))

        # We always return something from a page object, 
        # even if it's the same page object instance we are
        # currently on.
        return index


    @robot_alias("search__by__address")
    def search__by__address(self, term):
        index= self.type_in_search_box(term,"search address","xpath=/html/body/div[2]")
        self.click_element("xpath=/html/body/div[2]/div["+str (index)+"]")
        self.click_button("search button")
        ref_str = "no results matching your query"
        body_txt = self.get_text("css=body").encode("utf-8").lower()
        if  ref_str in body_txt: self.search__by__address(term)
        return self 


    @robot_alias("choose__veterinar")
    def choose__veterinar(self):
        # index= self.type_in_search_box(term,"search address","xpath=/html/body/div[2]")
        # self.click_element("xpath=/html/body/div[2]/div["+str (index)+"]")
        max_index = len(self.get_text("xpath=(//*[@id='react-form']/div/div[4]/div[2]/div[2]/div[1]/div/ul)").splitlines())/6
        index= randint(1, max_index)
        self.click_element("xpath=(//*[@id='el-" + str (index)+"']/div/div[2]/div/a)")
        sleep(10)
        return self



    @robot_alias("click__name__search_button")
    def click_search_button(self):
        self.click_button("search button")

        # When navigating to another type of page, return
        # the appropriate page object.
        return PubmedDocsumPage()


    @robot_alias("search__name__for")
    def search_for(self, term):
        self.type_in_search_box(term)
        return self.click_search_button()


    @robot_alias("switch__between__langauges")
    def switch_language(self):
        self.click_button("fr button")
        sleep(2)
        self.body_should_contain("Trouver un")
        self.click_button("en button")
        sleep(2)
        return self


    @robot_alias("clear_address_field")
    def clear_address_field(self):
        # self.type_in_search_box(self.random_value(), "search address","xpath=/html/body/div[2]" )
        self.input_text("search address", self.random_value())
        sleep(5)
        self.click_element("remove location")
        sleep(2)
        return self


    @robot_alias("clear_name_field")
    def clear_name_field(self):
        self.input_text("search name", self.random_value())
        sleep(3)
        self.click_element("remove name")
        self.click_element("remove name")
        sleep(3)
        return self


    @robot_alias("all__elements__on__page")
    def all_elements(self):
        print(self.page_should_contain_image("css=(http://vetdoc.co/static/images/bg_vet_directory.jpg)"))
        return self


    @robot_alias("switch__between__clinics__and__veterinarians")
    def switch_categories(self):
        self.click_element("switch button")
        sleep(2)
        self.click_element("choose clinic")
        sleep(4)
        self.click_element("switch button")
        sleep(2)
        self.click_element("choose veterinars")
        return self


    @robot_alias("__name__body_should_contain")
    def body_should_contain(self, str, ignore_case=True):
        ref_str = str.lower() if ignore_case else str
        ref_str = ref_str.encode("utf-8")
        body_txt = self.get_text("css=body").encode("utf-8").lower()
        asserts.assert_true(ref_str in body_txt, "body text does not contain %s" %ref_str)
        return self

class PubmedDocsumPage(Page):
    """Models a Pubmed search result page. For example:
    http://www.ncbi.nlm.nih.gov/pubmed?term=cat """

    uri = "/?location={location}"

    # This is a "selector template". We are parameterizing the 
    # nth result in this xpath. We call this from click_result, below.
    selectors = {
        "nth result link": "xpath=(//div[@class='rslt'])[{n}]/p/a",
    }

    @robot_alias("click_result_on__name__")
    def click_result(self, i):

        # For selector templates, we need to resolve the selector to the
        # locator first, before finding or acting on the element.
        locator = self.resolve_selector("nth result link", n=int(i))
        self.click_link(locator)
        return PubmedArticlePage()

class PubmedArticlePage(Page):

    uri = "/pubmed/{article_id}"

    @robot_alias("__name__body_should_contain")
    def body_should_contain(self, str, ignore_case=True):
        ref_str = str.lower() if ignore_case else str
        ref_str = ref_str.encode("utf-8")
        body_txt = self.get_text("css=body").encode("utf-8").lower()
        asserts.assert_true(ref_str in body_txt, "body text does not contain %s" %ref_str)
        return self