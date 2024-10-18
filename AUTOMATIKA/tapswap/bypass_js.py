from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from threading import Lock

class SingletonDriver:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(SingletonDriver, cls).__new__(cls, *args, **kwargs)
                    cls._instance.driver = cls._instance._init_driver()
        return cls._instance

    def _init_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # запускаем в фоновом режиме
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    @property
    def get_driver(self):
        return self.driver

    def execute_script(self, chq):
    
        
        self.driver.execute_script("""
class ChqService {
    static execute(value) {
        const len = value.length
          , bytes = new Uint8Array(len / 2)
          , x = 157;
        for (let R = 0; R < len; R += 2)
            bytes[R / 2] = parseInt(value.substring(R, R + 2), 16);
        const xored = bytes.map(R=>R ^ x)
          , decoded = new TextDecoder().decode(xored);
        return eval(decoded)
    }
}
""")

        result = self.driver.execute_script(f"""
var chrStub = document.createElement("div");
chrStub.id = "_chr_";
document.body.appendChild(chrStub);

class ChqService {{
    static execute(value) {{
        const len = value.length
          , bytes = new Uint8Array(len / 2)
          , x = 157;
        for (let R = 0; R < len; R += 2)
            bytes[R / 2] = parseInt(value.substring(R, R + 2), 16);
        const xored = bytes.map(R=>R ^ x)
          , decoded = new TextDecoder().decode(xored);
        return eval(decoded)
    }}
}}
            
try {{
    return ChqService.execute(`{chq}`);
}} catch (e) {{
    console.log(e);
    return e;
}}
        """)
        return result

    def __del__(self):
        if self.driver_context:
            self.driver_context.__exit__(None, None, None)

driver_instance = SingletonDriver()
