# Инициализация API #

    api = Api(host='http://127.0.0.1:8000', token='1CVVW76E4H88ABWA5E9E', appid='admc')


# В API находятся entrypoint-объекты #

    api.attributes  # используется для работы с атрибутами
    api.categories  # используется для работы с категориями
    api.files  # используется для работы с файлами
    api.folders  # используется для работы с папками
    api.products  # используется для работы с продуктами

# Получение списка объектов #
 
    attributes_list = api.attributes.list(maximum_items=100)

list() получает данные и сохраняет их в кеше. Принимает все возможные параметры,
которые описаны в [Документации](https://brandquad.atlassian.net/wiki/spaces/BD/pages/120651780/Public+API+v2), кроме них можно задать force=True,
для принудительной загрузки данных и обновления кеша, и maximum_items для ограничения
количества получаемых объектов, однако, когда maximum_items=150, а page_size=100,
то будет получено и сохранено 200 объектов.

# Получение по идентификатору, изменение, сохранение, удаление #

    attr = api.attributes.get(118)  # получение атрибута с id 118
    attr.position_in_group = 223  # изменение поля у атрибута
    attr.save()  # сохранение атрибута

    folder_13 = api.folders.get(13)

    file = api.files.get(2)
    file.folder = folder_13  # в случае, когда необходимо присвоить идентификатор, можно присвоить объект,

    cat_16 = api.categories.get(16)
    cat_18 = api.categories.get(18)

    cat_16.parent = cat_18
    cat_16.delete()

При сохранении продуктов перезаписывается информация измененная в поле attributes,
в отличие от всех остальных объектов

    product = api.products.get('1234235')
    product.attributes.update({'Тип': 'Другой тип'})
    product.save()
    
Так же можно вызывать методы save и delete не у самого объекта, а у entrypoint-объектов, тогда
при вызове методы save будут сохранены только те объекты, которые были изменены,
а при вызове delete будут удалены все закешированные объекты, находящиеся в entrypoint.items.
У метода delete есть параметр leave_in_cache, по умолчанию False, если True,
то объекты будут удалены с сервера, но останутся в кеше в entrypoint.items.

    product_list = api.products.list(page_size=3, maximum_items=3)
    for i, item in enumerate(product_list):
        product_list.get(item).attributes.update({'Тип': 'Тип {}'.format(i)})
        if i == 1:
            break

    products.save()  # будут сохранены только 1 и 2 продукты, а третий нет, так как он не изменялся
    products.delete()  # будут удалены все товары которые есть в кеше

# Вложенные entrypoint-объекты
У некоторых объектов есть в качестве атрибутов entrypoint-объекты

    folder = api.folders.get(1)
    folder.files  # используется для работы с файлами находящимися в конкретной папке

    file = api.files.get(1)
    file.links  # используется для работы со связями файла с продуктом

    product = api.products.get('1234567')
    product.assets  # используется для работы со связями продукта с файлом
    product.relations  # используется для работы со связанными товарами
    product.set  # используется для работы с продуктами, находящимися в наборе

Когда вы создаете новый объект, вам может потребоваться информация о возможных и необходимых полях, ее можно найти в поле help_fields объекта.
Значения этих полей нового объекта — None, по умолчанию.

    product = api.products.get('1234235')
    new = product.categories.new()
    print(new.category)  # --> None
    print(new.help_fields)  # --> "category": {
                            #              "type": "id",
                            #              "required": true,
                            #              "read_only": false,
                            #              "label": "Category id"
                            #      }

    new.category = 16
    print(new.category)  # --> 16
    new.save()  # теперь продукт относится к этой категории
    cat = product.categories.get(16)
    cat.delete()  # теперь продукт не относится к этой категории

Всю дополнительную информацию можно узнать в [Документации](https://brandquad.atlassian.net/wiki/spaces/BD/pages/120651780/Public+API+v2).
