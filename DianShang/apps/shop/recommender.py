import redis
from django.conf import settings
from .models import Product
'''
商品推荐模块功能：
  我们将基于历史销售来推荐商品，这样就可以辨别出哪些商品通常是一起购买的了。
  推荐给用户一些基于他们添加到购物车的产品。我们将会在 Redis 中为每个产品储存一个键（key）。产品的键将会和它的评分一同储存在 Redis 的有序集中。
  在一次新的订单被完成时，我们每次都会为一同购买的产品的评分加一。
  当一份订单付款成功后，我们保存每个购买产品的键，包括同意订单中的有序产品集。这个有序集让我们可以为一起购买的产品打分。
'''

# connect to redis
r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB)


class Recommender(object):

    def get_product_key(self, id):
        return 'product:{}:purchased_with'.format(id)

    '''
    products_bought 功能
    1. 得到所给 `Product` 对象的产品 ID
    2. 迭代所有的产品 ID。对于每个 `id` ，我们迭代所有的产品 ID 并且跳过所有相同的产品，这样我们就可以得到和每个产品一起购买的产品。
    3. 我们使用 `get_product_id()` 方法来获取 Redis 产品键。对于一个 ID 为 33 的产品，这个方法返回键 `product:33:purchased_with` 。
      这个键用于包含和这个产品被一同购买的产品 ID 的有序集。
    4. 我们把有序集中的每个产品 `id` 的评分加一。评分表示另一个产品和所给产品一起购买的次数。
    '''
    def products_bought(self, products):
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                # get the other products bought with each product
                if product_id != with_id:
                    # increment score for product purchased together
                    r.zincrby(self.get_product_key(product_id),
                              with_id,
                              amount=1)
    '''
    suggest_product_for() 方法接收下列参数：
        products：这是一个 Product 对象列表。它可以包含一个或者多个产品
        max_results：这是一个整数，用于展示返回的推荐的最大数量
        在这个方法中，我们执行以下的动作：
        1. 得到所给 `Product` 对象的 ID
        2. 如果只有一个产品，我们就检索一同购买的产品的 ID，并按照他们的购买时间来排序。这样做，我们就可以使用 Redis 的 `ZRANGE` 命令。
        我们通过 `max_results` 属性来限制结果的数量。
        3. 如果有多于一个的产品被给予，我们就生成一个临时的和产品 ID 一同创建的 Redis 键。
        4. 我们把包含在每个所给产品的有序集中东西的评分组合并相加，我们使用 Redis 的 `ZUNIONSTORE` 命令来实现这个操作。
        `ZUNIONSTORE` 命令执行了对有序集的所给键的求和，然后在新的 Redis 键中保存每个元素的求和。我们在临时键中保存分数的求和。
        你可以在这里阅读更多关于这个命令的信息：http://redisio/commands/ZUNIONSTORE 。
        5. 因为我们已经求和了评分，我们或许会获取我们推荐的重复商品。我们就使用 `ZREM` 命令来把他们从生成的有序集中删除。
        6. 我们从临时键中检索产品 ID，使用 `ZREM` 命令来按照他们的评分排序。我们把结果的数量限制在 `max_results` 属性指定的值内。
        然后我们删除了临时键。
        7. 最后，我们用所给的 `id` 获取 `Product` 对象，并且按照同样的顺序来排序。
    '''

    def suggest_products_for(self, products, max_results=6):
        product_ids = [p.id for p in products]
        if len(products) == 1:
            # only 1 product
            suggestions = r.zrange(self.get_product_key(product_ids[0]), 0, -1, desc=True)[:max_results]
        else:
            # generate a temporary key
            flat_ids = ''.join([str(id) for id in product_ids])
            tmp_key = 'tmp_{}'.format(flat_ids)
            # multiple products, combine scores of all products
            # store the resulting sorted set in a temporary key
            keys = [self.get_product_key(id) for id in product_ids]
            r.zunionstore(tmp_key, keys)
            # remove ids for the products the recommendation is for
            r.zrem(tmp_key, *product_ids)
            # get the product ids by their score, descendant sort
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_results]
            # remove the temporary key
            r.delete(tmp_key)
        suggested_products_ids = [int(id) for id in suggestions]

        # get suggested products and sort by order of appearance
        suggested_products = list(Product.objects.filter(id__in=suggested_products_ids))
        suggested_products.sort(key=lambda x: suggested_products_ids.index(x.id))
        return suggested_products

    def clear_purchases(self):
        for id in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id))
