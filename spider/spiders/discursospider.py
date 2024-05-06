import scrapy, re, csv, json
from datetime import datetime
from scrapy.exceptions import CloseSpider
from scrapy.crawler import CrawlerProcess

URL_CASA_ROSADA = "www.casarosada.gob.ar"
URL_DISCURSOS = "https://www.casarosada.gob.ar/informacion/discursos"

def obtener_orador(titulo, fecha, presidentes):    
    orador = next((presidente['nombre'] for presidente in presidentes if presidente['nombre'] in titulo), 'Indefinido')
    
    if orador == 'Indefinido' and fecha is not None:
        for info in presidentes:
            desde = datetime.strptime(info['desde'], '%d/%m/%Y')
            hasta = datetime.now() if info['hasta'] == 'Presente' else datetime.strptime(info['hasta'], '%d/%m/%Y')
            fecha_discurso = datetime.strptime(fecha, '%d/%m/%Y')

            if desde <= fecha_discurso <= hasta:
                orador = info['nombre']
                break

    return orador

def limpiar_pagrafo(pagrafo):
    lista = ['\xa0', '(APLAUSOS)', '(INAUDIBLE)', '(APLAUSO)', '\r', '\r\n', '\n', 'PERIODISTA.- ', 'PRESIDENTE.- ', '(…)']
    for i in lista:
        pagrafo = pagrafo.replace(i, '')
    return pagrafo

def parsear_fecha(fecha, meses):
    # Definir el patrón de expresión regular para extraer la fecha
    patron = r'(\w+)\s(\d+) de (\w+) de (\d+)'
    matches = re.search(patron, fecha, re.IGNORECASE)

    if matches:
        dia = matches.group(2)
        mes = matches.group(3)
        año = matches.group(4)
        return f"{dia.zfill(2)}/{meses[mes]}/{año}"
    else:
        return None

class DiscursoSpider(scrapy.Spider):
    name = "discursospider"
    allowed_domains = [URL_CASA_ROSADA]
    start_urls = [URL_DISCURSOS]

    def __init__(self, *args, **kwargs):
        super(DiscursoSpider, self).__init__(*args, **kwargs)
        self.data_list = []

        with open('fecha.txt', 'r') as f:
            self.ultima_actualizacion = datetime.strptime(f.readline().strip(), '%d/%m/%Y')

        self.nueva_actualizacion = self.ultima_actualizacion

        with open('app/src/presidentes.json', 'r') as file:
            self.presidentes = json.load(file)

        with open('meses.json', 'r') as file:
            self.meses = json.load(file)

    def parse(self, response):
        items = response.css('div.item[itemprop="blogPost"][itemscope][itemtype="http://schema.org/BlogPosting"]')
            
        for item in items:
            href = item.css('a.panel::attr(href)').get()
            yield response.follow(href, callback=self.parse_item)

        if response.css('li.pagination-next'):
            siguiente_url = response.urljoin(response.css('li.pagination-next a::attr(href)').get())
            yield scrapy.Request(siguiente_url, callback=self.parse)

    def parse_item(self, response):
        discurso = response.css('div.col-md-8.col-md-offset-2')
        pagrafos = discurso.css('p::text').getall()
        texto = [limpiar_pagrafo(pagrafo) for pagrafo in pagrafos if pagrafo.strip()]
        texto_final = ' '.join(texto)
        
        fecha = parsear_fecha(response.css('time.pull-right::text').get(), self.meses)
        
        if fecha is None:
            return

        fecha_datetime = datetime.strptime(fecha, '%d/%m/%Y')
        titulo = response.css('title::text').get()
        orador = obtener_orador(titulo, fecha, self.presidentes)

        if fecha_datetime > self.ultima_actualizacion: 
            if fecha_datetime > self.nueva_actualizacion:
                self.nueva_actualizacion = fecha_datetime

            if (orador != "Indefinido") and (len(texto_final) > 0):
                data = {
                    'orador': orador,
                    'fecha': fecha,
                    'discurso': texto_final
                }
            
                self.data_list.append(data)
                yield data

        else:
            raise CloseSpider('Actualización terminada')

    def close(self, reason):
        with open('discursos.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['orador', 'fecha', 'discurso'])
            writer.writerows(self.data_list)

        if self.nueva_actualizacion is not None and self.nueva_actualizacion > self.ultima_actualizacion:
            with open('fecha.txt', 'w') as f:
                f.write(self.nueva_actualizacion.strftime('%d/%m/%Y'))

if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(DiscursoSpider)
    process.start()