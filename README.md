# Simulador de SNP MC Systems con múltiples spikes

## Introducción

Este repositorio contiene el código de un intérprete y simulador de SNP MC Systems con múltiples spikes,
que he implementado como parte de mi TFM del master MIARFID, en este trabajo desarrollamos una variante 
del modelo presentado en [Spiking neural P systems with multiple channels](https://www.sciencedirect.com/science/article/pii/S0893608017301843),
obtenemos una serie de resultados teóricos e implementamos este simulador para poder hacer pruebas con el 
modelo más cómodamente.


## Lenguaje de especificación

Un ejemplo de programa que define un sistema:

```
# Definimos la neurona de entrada
input([0])

# Inicializamos el contenido de las neuronas
[1] = {'1'} * 3
[2] = {'1'} * 2

# Inicializamos las sinapsis y definimos a que canal pertenecen
<1> [5] --> [1]
<2> [0] --> [2]
<2> [5] --> [2]
<3> [5] --> [3]
<4> [5] --> [4]
<5> [2] --> [5]

# Añadimos las reglas de activación
[0] 'a' / {'a'} --> {'a'} <2>

[2] '1'* 'a' / {'1'} --> {'1'} <5>
[2] '1'* 'a' / {'a'} --> {'a'} <5>

[5] '1'* 'a' / {'1'} --> {'1'} <2>, {'1'} <1>
[5] '1'* 'a' / {'a'} --> {'a'} <3>
[5] '1'* 'a' / {'a'} --> {'a'} <4>
```

### Tipos de datos

Los dos tipos de datos básicos son los enteros, los símbolos (representados como cadenas python) y los multiconjuntos (representados como sets python). Los tipos de datos básicos se pueden almacenar en variables, por ejemplo ``n = 12``.

Además podemos trabajar con membranas (neuronas) que se representan como un entero entre corchetes (Ej.: ``[1]``), aunque en lugar de un literal se puede emplear una variable que contenga a ese literal, por ejemplo partiendo de la variable 
``n`` 
definida anteriormente, podemos acceder a la membrana 12 mediante ``[n]``.


### Operador de asignación

Los valores siempre se pasan por copia, por lo que si asignas un valor a una variable y modificas el valor de dicha variable, no modificas el valor original.

Las membranas son un caso especial, pues no se trata de un tipo básico. Si tratamos de asignar un valor a una membrana, lo que haremos en realidad es establecer el multiconjunto inicial de dicha membrana (sobra decir que solo se le puede asignar un valor de tipo multiconjunto). Si por el contrario tratamos de almacenar una membrana en una variable, copiaremos su multiconjunto.

Por lo tanto

```
[1] = {'a'}
b = [1]
```

es equivalente a

```
[1] = {'a'}
b = {'a'}
```


### Operadores aritméticos
En los siguientes apartados iremos explicando los distintos operadores que permite cada tipo de datos, a nivel general solo cabría destacar que el orden de las operaciones es el mismo que en la mayoría de los lenguajes:

Unarias (-) > Multiplicativas (/*%) > Aditivas (+-) > Lógicas (|&)


#### Enteros
Los enteros constan de los operadores básicos suma(+), resta(-), multiplicación(*), división(/) y módulo(%). El lenguaje no contempla números decimales, así que la división será entera (equivalente al operador // en python).


#### Símbolos (strings)
Los símbolos solo permiten dos operadores, la concatenación (+) que permite concatenar tanto símbolos como un símbolo y un entero.

```
'a' + 'a'    # 'aa'
'a' +  1     # 'a1'
 1  + 'a'    # '1a'
```

Y el producto (*), que solo se contempla entre un símbolo como parte izquierda y un entero como parte derecha.

```
'ab' *  3     # 'ababab'
 2   * 'a'    # Error
```

### Multiconjuntos
Sobre multiconjuntos está definida la unión(|), concatenación (+), intersección (&) y diferencia (-).

Por otro lado tendriamos el producto, que debe tener un multiconjunto ``m`` como parte izquierda y un entero ``n`` como 
parte derecha, y es equivalente a sumar ``n`` veces el multiconjunto ``m``.

Todas estas operaciones se verían de la siguiente manera en el código:
```
{'a', 'b'} | {'b', 'b'}         # {'a', 'b', 'b'}
{'a', 'b'} + {'b', 'b'}         # {'a', 'b', 'b', 'b'}
{'a', 'b'} & {'a', 'a'}         # {'a'}
{'a', 'a', 'b'} - {'a', 'c'}    # {'a', 'b'}
{'a', 'b'} * 2                  # {'a', 'a', 'b', 'b'}
```


### Neurona de entrada y salida al entorno

Si queremos marcar una neurona como entrada, podemos emplear la función 
``input()``, que recibe como único parámetro la neurona de entrada (Ej.: ``input([2])``).

Por otro lado, para referirnos al entorno o neurona de salida, podemos usar la palabra reservada 
``out``.


### Canales

Para definir un canal y/o añadirle una sinapsis, empleamos la sintaxis:

```
canal salida --> destino
```

Es importante tener en cuenta que el canal debe ir entre ``<`` y ``>``, y que 
``salida`` y ``destino``
deben ser membranas. Por ejemplo, si queremos crear dos sinapsis en el canal 0, que salen de la membrana 1, 
una llega a la membrana 2 y la otra al entorno, escribiríamos:

```
<0> [1] --> [2]
<0> [1] --> out
```


### Reglas de activación

Para añadir una regla de activación a una membrana empleamos la sintaxis:

<code>
membrana regex / consumido --> enviado<sub>1</sub> canal<sub>1</sub>, enviado<sub>2</sub> canal<sub>2</sub>, ... : delay
</code>

Donde ``membrana``
es la membrana donde se encuentra la regla, ``regex``
es la expresión regular de dicha regla, ``consumido``
es el multiconjunto que consume, <code>enviado<sub>i</sub></code>
es el multiconjunto que envía por el canal <code>canal<sub>i</sub></code>
y ``delay`` es el delay de la regla.

La regla de activación debe tener como mínimo un par <code>enviado<sub>1</sub> canal<sub>1</sub></code>, pero hay otra 
información que se puede omitir, como la expresión regular (en cuyo caso será igual al multiset consumido) y el 
delay (``delay = 0``), dejando la regla con la forma:

<code>
membrana consumido --> enviado<sub>1</sub> canal<sub>1</sub>, enviado<sub>2</sub> canal<sub>2</sub>, ...
</code>

Es importante notar que al omitir la expresión regular también se ha omitido la contrabarra, si se deja, el sistema 
interpretará que la expresión regular es λ, lo que hará la regla inaplicable.

### Expresión regular

La expresión regular permite el uso de paréntesis, el operador uno o más (+) y el operador cero o más (*), para especificar los símbolos, se deben poner entre comillas.

Ejemplos:

<pre><code>'a'+ 'b'         # <code>a<sup>+</sup>b</code>
('b''a'+)'b'*    # ba<sup>+</sup>b<sup>*</sup>
('b''a')+'b'*    # (ba)<sup>+</sup>b<sup>*</sup>
</code></pre>

Notese que una expresión regular es en ocasiones indistinguible de una operación entre símbolos (como en el primer caso), por lo tanto se asumirá que todo lo que se encuentra en una regla entre la membrana y la contrabarra es una expresión regular.


### Reglas de olvido
Para las reglas de olvido se hace uso de la palabra reservada ``lambda``, siguiendo la sintaxis:
```
membrana consumido --> lambda
```

Donde ``membrana`` es la membrana donde se encuentra la regla y ``consumido`` es el multiconjunto que consume.


## Uso del simulador

Si lanzamos el simulador con la opción ``--help``
, mostrará la siguiente ayuda:

```
Usage: main.py [OPTIONS] SRC

Options:
  -i, --input TEXT
  --separator TEXT
  --no-strip
  --render
  --render-path TEXT
  -r, --repeat INTEGER
  -m, --mode [halt|halt-mc|time|time-mc]
  --max-steps INTEGER
```

Donde aparte de ``SRC``, que es la ruta hasta el fichero donde se encuentra la especificación del modelo que se 
desea interpretar, se pueden especificar los siguientes parámetros opcionales:

- ``input``: Una cadena de caracteres que indica los símbolos que se encuentran en la neurona de entrada al inicio 
de la computación.
- ``separator``: El carácter de separación empleado en ``input``, por defecto la coma.
- ``no-strip``: Por defecto se eliminarán los espacios en blanco de los símbolos de entrada, si se usa esta flag, 
se mantendrán.
- ``render``: Al emplear esta flag se le indica a la aplicación que se desean renderizar cada una de las 
iteraciones del sistema.
- ``render-path``: Directorio donde se desean guardar los renders (solo se emplea si se ha usado la flag ``render``).
- ``repeat``: Número de veces que se desea repetir la ejecución.
- ``mode``: Modo de lectura de la salida (``halt`` por defecto).
- ``max-steps``: Máximo número de iteraciones (fuerza la parada de ejecuciones que la superen).


## Instalación

El único requisito para realizar la instalación es tener ``python 3.10.8`` instalado.

Una vez tenemos python instalado clonamos el repositorio:

``git clone https://github.com/RodrigoLlanes/SNP-MC-MS-Systems-simulator``

Nos movemos a dentro de la carpeta:

``cd SNP-MC-MS-Systems-simulator``

Creamos un entorno virtual, lo activamos e instalamos las dependencias:

```
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Una vez instaladas dichas dependencias comprobamos que todo se haya instalado correctamente:

```
python test.py
```

Y si no hemos obtenido ningún error podemos ejecutar el simulador:

```
python .\main.py -i "a" --render .\tests\src\reg-add.txt 
```

Si todo ha ido bien el programa debería devolver ``()`` o ``(a * 1)`` debido a que la salida del ejemplo 
``.\tests\src\reg-add.txt`` es indeterminista.

En la carpeta ``tmp`` tendrás una versión renderizada de cada instante de tiempo de la ejecución donde verás la 
evolución del sistema.

A partir de aquí ya puedes modificar los ejemplos que se encuentran en ``test/src`` o crear tus propios modelos y
empezar a experimentar con las opciones del simulador.