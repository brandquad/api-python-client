import brandquad_sdk
import unittest


class SdkTestCase(unittest.TestCase):
    def test_smoke(self):
        api = brandquad_sdk.api.Api(host='http://127.0.0.1:8000/', token='1CVVW76E4H88ABWA5E9E', appid='admc')

        attributes = api.attributes
        attr_list = attributes.list(maximum_items=100)
        assert isinstance(attr_list, brandquad_sdk.entity.SlicableOrderedDict)
        assert not attributes.error

        types = attributes.types
        type_list = types.list(maximum_items=100)
        assert isinstance(type_list, brandquad_sdk.entity.SlicableOrderedDict)
        assert not types.error

        groups = attributes.groups
        group_list = groups.list(maximum_items=100)
        assert isinstance(group_list, brandquad_sdk.entity.SlicableOrderedDict)
        assert not groups.error

        files = api.files
        file_list = files.list(maximum_items=100)
        assert isinstance(file_list, brandquad_sdk.entity.SlicableOrderedDict)
        assert not files.error

        file = None
        for f in file_list:
            file = files.get(f)
            break

        links = file.links
        link_list = links.list()
        assert isinstance(link_list, brandquad_sdk.entity.SlicableOrderedDict)
        assert not links.error

        folders = api.folders
        folder_list = folders.list(maximum_items=100)
        assert isinstance(folder_list, brandquad_sdk.entity.SlicableOrderedDict)
        assert not folders.error

        folder = None
        for f in folder_list:
            folder = folders.get(f)
            break

        if folder:
            files_in_folder = folder.files.list(maximum_items=100)
            assert isinstance(files_in_folder, brandquad_sdk.entity.SlicableOrderedDict)

        categories = api.categories
        category_list = categories.list(maximum_items=100)
        assert isinstance(category_list, brandquad_sdk.entity.SlicableOrderedDict)
        assert not categories.error

        products = api.products
        product_list = products.list(maximum_items=100)
        assert isinstance(product_list, brandquad_sdk.entity.SlicableOrderedDict)
        assert not products.error

        product = None
        for p in product_list:
            product = products.get(p)
            product.attributes['Тип'] = 'sdfsd'

        prod_categories = product.categories
        prod_cat_list = prod_categories.list(maximum_items=100)
        assert isinstance(prod_cat_list, brandquad_sdk.entity.SlicableOrderedDict)
        assert not prod_categories.error

        prod_assets = product.assets
        prod_asset_list = prod_assets.list(maximum_items=100)
        assert isinstance(prod_asset_list, brandquad_sdk.entity.SlicableOrderedDict)
        assert not prod_assets.error

        prod_relations = product.relations
        prod_relation_list = prod_assets.list(maximum_items=100)
        assert isinstance(prod_relation_list, brandquad_sdk.entity.SlicableOrderedDict)
        assert not prod_relations.error

        prods_in_set = product.set
        prods = prods_in_set.list(maximum_items=100)
        assert isinstance(prods, brandquad_sdk.entity.SlicableOrderedDict)
        assert (not prods_in_set.error or prods_in_set.error != 'This is a set')


if __name__ == '__main__':
    unittest.main()
