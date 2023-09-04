import scrapy

class PokeSpider(scrapy.Spider):
  name = 'pokespider'
  start_urls = ['https://pokemondb.net/pokedex/all']

  def parse(self, response):
    table_pokedex = "table#pokedex > tbody > tr"

    lines = response.css(table_pokedex)
    
    for line in lines:
      link = line.css("td:nth-child(2) > a::attr(href)")
      yield response.follow(link.get(), self.parse_pokemon)

  def parse_pokemon(self, response):
    number_pokemon = response.css('table.vitals-table > tbody > tr:nth-child(1) > td > strong::text')
    name_pokemon = response.css('.main-content > h1::text')
    weight_pokemon = response.css('table.vitals-table > tbody > tr:nth-child(5) > td::text')
    height_pokemon = response.css('table.vitals-table > tbody > tr:nth-child(4) > td::text')
    first_type_pokemon = response.css('table.vitals-table > tbody > tr:nth-child(2) > td > a:nth-child(1)::text')
    second_type_pokemon = response.css('table.vitals-table > tbody > tr:nth-child(2) > td > a:nth-child(2)::text')

    pokemon_info = {
      'id': number_pokemon.get(), 
      'url': response.request.url,
      'name': name_pokemon.get(), 
      'weight': weight_pokemon.get(), 
      'height': height_pokemon.get(),
      'first_type': first_type_pokemon.get(), 
      'second_type': second_type_pokemon.get(),
      'evolutions': [],
      'abilities': []
    }

    cont = 1
    evolutions = []
    while(True):
      if cont % 2 == 1:
        evolution_data = response.css(f'.infocard-list-evo > div:nth-child({cont}) > span.infocard-lg-img > a::attr(href)')
        poke_num = response.css(f'.infocard-list-evo > div:nth-child({cont}) > span.infocard-lg-data > small::text')
        name = response.css(f'.infocard-list-evo > div:nth-child({cont}) > span.infocard-lg-data > a.ent-name::text')
        if evolution_data and poke_num and name:
          evolutions.append({
            'pokeNum': poke_num.get(),
            'evolution_url': evolution_data.get(),
            'name': name.get()
          })
        else:
          print("break")
          break
      cont += 1
    pokemon_info['evolutions'] = evolutions
    
    cont = 1
    ability_data = []
    while(True):
      if cont % 2 == 1:
        ability_link = response.css(f'table.vitals-table > tbody > tr:nth-child(6) > td > .text-muted:nth-child({cont}) > a::attr(href)').get()
        if ability_link:
          ability_data.append(ability_link)
        else:  
          print("break")
          break
      cont += 1
      
    yield response.follow(ability_data[0], self.parse_ability, meta={'pokemon_info': pokemon_info, 'next_links': ability_data})
  
  def parse_ability(self, response):
    pokemon_info = response.meta['pokemon_info']
    next_links = response.meta['next_links']
    next_links.pop(0)
    
    url_ability = response.request.url
    name_ability = response.css('#main > h1::text')
    effect_ability = response.css('#main > div.grid-row > div:nth-child(1) > p:nth-child(2)::text')

    pokemon_info['abilities'].append({
      'ability_url': url_ability,
      'name_ability': name_ability.get(),
      'effect_ability': effect_ability.get()
    })

    if len(next_links) > 0:
      yield response.follow(next_links[0], self.parse_ability, meta={'pokemon_info': pokemon_info, 'next_links': next_links})
    else:
      yield pokemon_info
    pass
      