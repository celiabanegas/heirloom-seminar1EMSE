"""Built-in catalog of classic recipes. Loaded into Postgres on first start; users copy them into their
cookbooks and then edit their own copy. All quantities in metric units."""

CATEGORIES = ["Entrantes", "Principales", "Pescados", "Legumbres", "Arroces y pasta", "Postres", "Desayunos"]

# Recipes copied into a new cookbook when "start with some classics" is ticked.
STARTER_TITLES = ["Tortilla de patatas", "Lentejas estofadas", "Gazpacho andaluz", "Arroz con leche"]

RECIPES = [
    {
        "title": "Tortilla de patatas",
        "category": "Principales",
        "servings": 4,
        "minutes": 45,
        "ingredients": """6 huevos
700 g de patatas
1 cebolla mediana
200 ml de aceite de oliva virgen extra
Sal""",
        "steps": """Pelar las patatas y cortarlas en láminas finas; picar la cebolla en juliana.
Pochar patata y cebolla en el aceite a fuego medio-bajo unos 20 minutos, hasta que estén tiernas sin dorarse.
Escurrir bien el aceite y salar.
Batir los huevos con una pizca de sal y mezclar con la patata; dejar reposar 5 minutos.
Cuajar en una sartén con 1 cucharada de aceite, 3 minutos por cada lado, dando la vuelta con un plato.""",
    },
    {
        "title": "Gazpacho andaluz",
        "category": "Entrantes",
        "servings": 4,
        "minutes": 15,
        "ingredients": """1 kg de tomates maduros
1 pimiento verde italiano
1/2 pepino
1 diente de ajo
50 g de pan del día anterior
80 ml de aceite de oliva virgen extra
20 ml de vinagre de Jerez
Sal
200 ml de agua fría""",
        "steps": """Lavar y trocear tomates, pimiento y pepino pelado.
Remojar el pan en un poco de agua.
Triturar todas las verduras con el ajo, el pan, el vinagre y la sal.
Añadir el aceite poco a poco sin dejar de triturar, para que emulsione.
Colar si se quiere más fino, ajustar con agua fría y enfriar al menos 2 horas.""",
    },
    {
        "title": "Salmorejo cordobés",
        "category": "Entrantes",
        "servings": 4,
        "minutes": 15,
        "ingredients": """1 kg de tomates pera maduros
200 g de pan de miga densa
1 diente de ajo pequeño
150 ml de aceite de oliva virgen extra
Sal
2 huevos cocidos y 60 g de jamón serrano para servir""",
        "steps": """Triturar los tomates y colarlos.
Añadir el pan troceado y dejarlo empapar 10 minutos.
Triturar con el ajo y la sal hasta que quede muy fino.
Incorporar el aceite en hilo sin dejar de batir hasta que espese.
Enfriar y servir con huevo cocido picado y tiras de jamón.""",
    },
    {
        "title": "Croquetas de jamón",
        "category": "Entrantes",
        "servings": 6,
        "minutes": 90,
        "ingredients": """100 g de jamón serrano picado
1/2 cebolla
80 g de mantequilla
90 g de harina de trigo
800 ml de leche entera
Nuez moscada y sal
2 huevos y 150 g de pan rallado para rebozar
Aceite de oliva para freír""",
        "steps": """Pochar la cebolla muy picada en la mantequilla; añadir el jamón y rehogar 1 minuto.
Agregar la harina y tostarla 3 minutos removiendo.
Verter la leche caliente poco a poco, sin dejar de remover, hasta tener una bechamel espesa (unos 15 minutos).
Sazonar con nuez moscada, pasar a una fuente, tapar a piel y enfriar en la nevera al menos 4 horas.
Formar las croquetas, pasarlas por huevo batido y pan rallado.
Freír en aceite bien caliente (180 °C) hasta que estén doradas.""",
    },
    {
        "title": "Lentejas estofadas",
        "category": "Legumbres",
        "servings": 4,
        "minutes": 60,
        "ingredients": """300 g de lentejas pardinas
1 chorizo
1 cebolla
1 pimiento verde
2 zanahorias
1 patata mediana
2 dientes de ajo
1 hoja de laurel
1 cucharadita de pimentón dulce
1,5 l de agua
Aceite de oliva y sal""",
        "steps": """Lavar las lentejas (las pardinas no necesitan remojo).
Sofreír cebolla, pimiento, ajo y zanahoria picados en aceite durante 10 minutos.
Añadir el chorizo en rodajas y el pimentón, y rehogar 1 minuto sin que se queme.
Incorporar las lentejas, el laurel y el agua fría; cocer a fuego suave 30 minutos.
Añadir la patata cascada y cocer 15 minutos más. Salar y dejar reposar 5 minutos.""",
    },
    {
        "title": "Garbanzos con espinacas",
        "category": "Legumbres",
        "servings": 4,
        "minutes": 30,
        "ingredients": """600 g de garbanzos cocidos
300 g de espinacas frescas
3 dientes de ajo
40 g de pan
1 cucharadita de comino molido
1 cucharadita de pimentón dulce
20 ml de vinagre de Jerez
200 ml de caldo de verduras
Aceite de oliva y sal""",
        "steps": """Freír en aceite los ajos laminados y el pan hasta que estén dorados; reservar.
Saltear las espinacas en la misma sartén hasta que reduzcan.
Majar los ajos y el pan con el comino, el pimentón y el vinagre.
Añadir los garbanzos, el majado y el caldo a las espinacas.
Cocer 10 minutos a fuego suave y ajustar de sal.""",
    },
    {
        "title": "Paella valenciana",
        "category": "Arroces y pasta",
        "servings": 4,
        "minutes": 75,
        "ingredients": """400 g de arroz bomba
500 g de pollo troceado
300 g de conejo troceado
200 g de judía verde plana
150 g de garrofón
1 tomate rallado
1 cucharadita de pimentón dulce
Unas hebras de azafrán
1,2 l de agua
1 ramita de romero
100 ml de aceite de oliva y sal""",
        "steps": """Dorar bien el pollo y el conejo salados en el aceite, a fuego medio, unos 15 minutos.
Añadir la judía y el garrofón y rehogar 5 minutos.
Hacer hueco en el centro, sofreír el tomate y añadir el pimentón.
Verter el agua con el azafrán y cocer 20 minutos; ajustar de sal.
Repartir el arroz en cruz, extender y cocer 10 minutos a fuego fuerte y 8 a fuego suave sin remover.
Poner el romero los últimos minutos, dejar socarrar 1 minuto y reposar 5 minutos tapada con un paño.""",
    },
    {
        "title": "Espaguetis carbonara",
        "category": "Arroces y pasta",
        "servings": 4,
        "minutes": 20,
        "ingredients": """400 g de espaguetis
150 g de guanciale (o panceta curada)
4 yemas y 1 huevo entero
80 g de queso pecorino romano rallado
Pimienta negra recién molida""",
        "steps": """Cocer la pasta en agua con sal.
Dorar el guanciale en tiras en una sartén sin aceite hasta que suelte la grasa.
Batir las yemas y el huevo con el pecorino y mucha pimienta.
Escurrir la pasta guardando 100 ml del agua de cocción y mezclarla con el guanciale fuera del fuego.
Añadir la mezcla de huevo y un poco de agua de cocción, removiendo rápido hasta tener una crema (sin que cuaje).""",
    },
    {
        "title": "Risotto de setas",
        "category": "Arroces y pasta",
        "servings": 4,
        "minutes": 35,
        "ingredients": """320 g de arroz arborio o carnaroli
300 g de setas variadas
1 chalota
100 ml de vino blanco
1 l de caldo de verduras caliente
40 g de mantequilla
60 g de parmesano rallado
Aceite de oliva y sal""",
        "steps": """Saltear las setas troceadas con aceite y sal; reservar.
Pochar la chalota picada, añadir el arroz y nacararlo 2 minutos.
Mojar con el vino y dejar que se evapore.
Añadir el caldo cazo a cazo, removiendo, durante unos 18 minutos.
Incorporar las setas, apagar el fuego y mantecar con la mantequilla y el parmesano. Reposar 2 minutos.""",
    },
    {
        "title": "Pisto manchego",
        "category": "Principales",
        "servings": 4,
        "minutes": 60,
        "ingredients": """2 cebollas
1 pimiento rojo
1 pimiento verde
2 calabacines
800 g de tomate triturado
1 cucharadita de azúcar
80 ml de aceite de oliva
Sal
4 huevos (opcional, para servir)""",
        "steps": """Picar todas las verduras en dados del mismo tamaño.
Pochar la cebolla en el aceite 10 minutos; añadir los pimientos y cocinar 10 minutos más.
Incorporar el calabacín y rehogar 10 minutos.
Añadir el tomate, el azúcar y la sal, y cocer a fuego suave 25 minutos.
Servir con un huevo frito encima.""",
    },
    {
        "title": "Pollo al ajillo",
        "category": "Principales",
        "servings": 4,
        "minutes": 40,
        "ingredients": """1 kg de pollo troceado pequeño
10 dientes de ajo
150 ml de vino blanco
1 hoja de laurel
Perejil fresco
80 ml de aceite de oliva
Sal y pimienta""",
        "steps": """Salpimentar el pollo y dorarlo en el aceite a fuego medio unos 15 minutos.
Añadir los ajos sin pelar, ligeramente aplastados, y el laurel; cocinar 5 minutos.
Verter el vino y dejar reducir a fuego suave, tapado, unos 15 minutos.
Espolvorear con perejil picado antes de servir.""",
    },
    {
        "title": "Merluza en salsa verde",
        "category": "Pescados",
        "servings": 4,
        "minutes": 25,
        "ingredients": """4 lomos de merluza (unos 800 g)
500 g de almejas
4 dientes de ajo
1 cucharada de harina
100 ml de vino blanco
200 ml de caldo de pescado
Perejil fresco abundante
60 ml de aceite de oliva y sal""",
        "steps": """Poner las almejas en agua con sal 30 minutos para que suelten la arena.
Dorar ligeramente el ajo picado en el aceite, añadir la harina y tostar 1 minuto.
Verter el vino y el caldo poco a poco, moviendo la cazuela para ligar la salsa.
Añadir la merluza salada, con la piel hacia arriba, y las almejas; cocinar 5-6 minutos moviendo la cazuela.
Espolvorear abundante perejil picado y servir enseguida.""",
    },
    {
        "title": "Salmón al horno con limón",
        "category": "Pescados",
        "servings": 4,
        "minutes": 25,
        "ingredients": """4 lomos de salmón (unos 600 g)
1 limón
2 dientes de ajo
Eneldo fresco
30 ml de aceite de oliva
Sal y pimienta""",
        "steps": """Precalentar el horno a 200 °C.
Colocar el salmón en una bandeja, salpimentar y regar con aceite.
Repartir el ajo laminado, rodajas de limón y eneldo por encima.
Hornear 12-15 minutos, según el grosor, y terminar con zumo de limón.""",
    },
    {
        "title": "Hummus",
        "category": "Entrantes",
        "servings": 4,
        "minutes": 10,
        "ingredients": """400 g de garbanzos cocidos
60 g de tahini
1 limón (su zumo)
1 diente de ajo
50 ml de agua fría
30 ml de aceite de oliva
1/2 cucharadita de comino
Pimentón y sal""",
        "steps": """Triturar los garbanzos con el tahini, el zumo de limón, el ajo y el comino.
Añadir el agua fría poco a poco hasta que quede muy cremoso.
Ajustar de sal y limón.
Servir con un chorro de aceite y una pizca de pimentón.""",
    },
    {
        "title": "Curry de garbanzos",
        "category": "Legumbres",
        "servings": 4,
        "minutes": 35,
        "ingredients": """600 g de garbanzos cocidos
1 cebolla
2 dientes de ajo
20 g de jengibre fresco
2 cucharadas de curry en polvo
400 ml de leche de coco
400 g de tomate triturado
150 g de espinacas
Cilantro fresco, aceite y sal""",
        "steps": """Pochar la cebolla picada en aceite 8 minutos; añadir ajo y jengibre rallados.
Incorporar el curry y tostarlo 1 minuto.
Añadir el tomate y cocer 5 minutos.
Agregar la leche de coco y los garbanzos y cocer 15 minutos a fuego suave.
Añadir las espinacas al final y servir con cilantro y arroz basmati.""",
    },
    {
        "title": "Shakshuka",
        "category": "Desayunos",
        "servings": 2,
        "minutes": 25,
        "ingredients": """4 huevos
1 cebolla
1 pimiento rojo
2 dientes de ajo
400 g de tomate triturado
1 cucharadita de comino
1 cucharadita de pimentón dulce
Perejil o cilantro, aceite y sal""",
        "steps": """Sofreír la cebolla y el pimiento en tiras en aceite 10 minutos; añadir el ajo y las especias.
Incorporar el tomate y cocer 8 minutos hasta que espese.
Hacer cuatro huecos y cascar un huevo en cada uno.
Tapar y cocinar 5-6 minutos, hasta que la clara cuaje y la yema siga líquida.
Terminar con hierbas frescas y servir con pan.""",
    },
    {
        "title": "Tortitas americanas",
        "category": "Desayunos",
        "servings": 4,
        "minutes": 20,
        "ingredients": """200 g de harina de trigo
2 huevos
250 ml de leche
30 g de mantequilla derretida
25 g de azúcar
10 g de levadura química
Una pizca de sal""",
        "steps": """Mezclar la harina, el azúcar, la levadura y la sal.
Batir los huevos con la leche y la mantequilla derretida.
Unir ambas mezclas sin batir en exceso (algún grumo está bien) y reposar 5 minutos.
Cocinar cucharones de masa en una sartén antiadherente a fuego medio hasta que salgan burbujas; dar la vuelta 1 minuto.""",
    },
    {
        "title": "Arroz con leche",
        "category": "Postres",
        "servings": 6,
        "minutes": 60,
        "ingredients": """150 g de arroz redondo
1 l de leche entera
120 g de azúcar
1 rama de canela
Piel de 1 limón
Canela molida para servir""",
        "steps": """Calentar la leche con la canela y la piel de limón hasta que hierva.
Añadir el arroz y cocer a fuego muy suave 40 minutos, removiendo a menudo.
Incorporar el azúcar y cocer 5 minutos más.
Retirar la canela y el limón, repartir en cuencos y enfriar.
Espolvorear canela molida antes de servir.""",
    },
    {
        "title": "Flan de huevo",
        "category": "Postres",
        "servings": 6,
        "minutes": 70,
        "ingredients": """4 huevos
500 ml de leche entera
100 g de azúcar
1 cucharadita de extracto de vainilla
Para el caramelo: 100 g de azúcar y 30 ml de agua""",
        "steps": """Hacer un caramelo con el azúcar y el agua y repartirlo en el fondo de las flaneras.
Batir los huevos con el azúcar y la vainilla, añadir la leche templada y colar.
Rellenar las flaneras y hornear al baño maría a 160 °C unos 45 minutos.
Dejar enfriar y refrigerar al menos 4 horas antes de desmoldar.""",
    },
    {
        "title": "Bizcocho de yogur",
        "category": "Postres",
        "servings": 8,
        "minutes": 50,
        "ingredients": """125 g de yogur natural
3 huevos
200 g de azúcar
100 ml de aceite de girasol
250 g de harina de trigo
16 g de levadura química
Ralladura de 1 limón""",
        "steps": """Precalentar el horno a 180 °C y engrasar un molde de unos 22 cm.
Batir los huevos con el azúcar hasta que blanqueen.
Añadir el yogur, el aceite y la ralladura.
Incorporar la harina tamizada con la levadura con movimientos envolventes.
Hornear unos 35 minutos, hasta que un palillo salga limpio.""",
    },
    {
        "title": "Tarta de queso al horno",
        "category": "Postres",
        "servings": 8,
        "minutes": 60,
        "ingredients": """600 g de queso crema
4 huevos
200 g de azúcar
300 ml de nata para montar (35 % de grasa)
20 g de harina de trigo""",
        "steps": """Precalentar el horno a 220 °C y forrar un molde de 22 cm con papel de horno arrugado.
Batir el queso con el azúcar hasta que esté liso.
Añadir los huevos de uno en uno, luego la nata y por último la harina tamizada.
Hornear 30-35 minutos: debe quedar muy tostada por fuera y temblorosa en el centro.
Enfriar a temperatura ambiente y después en la nevera.""",
    },
]
