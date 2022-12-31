# FLT_lab5

## Задание

Cоставить атрибутную грамматику для описания контекстно-свободных грамматик (с атрибутами `isReachable`, `isGenerating`, `isNonEmpty`) и реализовать генератор случайных грамматик в пользовательском синтаксисе.

### Дополнительное задание

**Анализ грамматики**:

- Построить описание параметризированной грамматики
- Определить, к какому классу (LL(k), LR(k)) относится грамматика
- Проанализировать, при каком выборе значений токенов грамматика теряет свои свойства

Дополнительное задание лежит в файле [additional/lab_5_dop.pdf](https://github.com/pollykon/FLT_lab5/blob/main/additional/lab_5_dop.pdf)

**Атрибутная грамматика**: [additional/attribute_grammar.pdf](https://github.com/pollykon/FLT_lab5/blob/main/additional/attribute_grammar.pdf)

**Документация в Latex**: [documentation.pdf](https://github.com/pollykon/FLT_lab5/blob/main/documentation.pdf)

## Установка

```bash
git clone https://github.com/pollykon/FLT_lab5
cd FLT_lab5
pip install -r requirements.txt
```

## Запуск

Чтобы сгенерировать грамматику создайте конфиг-файл с параметрами конфигурации, либо используйте готовый, и запустите файл `generator.py`, направив поток входных данных из конфига.

```bash
python generator.py < configs/default.yaml
```

Можно запустить генератор с проверкой пользовательского синтаксиса на LL(1). Для этого используйте ключ `--check-ll1`

```bas
python generator.py --check-ll1 < configs/default.yaml
```

Более подробная [документация в latex](https://github.com/pollykon/FLT_lab5/blob/main/documentation.pdf)
