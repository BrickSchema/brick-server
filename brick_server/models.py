from pdb import set_trace as bp
import numbers

from mongoengine import Document, DynamicDocument
from mongoengine import StringField, DateTimeField, ListField, DictField, BooleanField
from mongoengine import ReferenceField, IntField
from mongoengine import connect as mongo_connect

from .configs import configs
from .exceptions import DoesNotExistError, MultipleObjectsFoundError

mongo_connect(
    db = configs['users']['dbname'],
    #username = configs['apps']['user'],
    #password = configs['apps']['password'],
    host = configs['users']['host'],
    connect=False,
)

DEFAULT_TOKEN_LIFETIME = 24 * 60 * 60 * 100 # 100 day in secounds TODO: This is only for dev
DEFAULT_PERMISSION_LIFETIME = 24 * 60 * 60 * 100 # 100 day in secounds TODO: This is only for dev.


async def get_all_relationships(sparql_db, entity_id):
    #TODO: Implement owl:inverseOf inside Vrituoso
    print('warning: ``inverseOf`` is not implemented yet inside Virtuoso')
    qstr = """
    select ?p ?o where {{
    {{
    <{0}> ?p ?o.
    FILTER NOT EXISTS {{ <{0}> a ?o .}}
    }}
    UNION
    {{
    ?inverse_p owl:inverseOf ?p .
    ?o ?inverse_p <{0}>.
    }}
    }}
    """.format(entity_id)
    res = await sparql_db.query(qstr)
    return [(row['p']['value'], row['o']['value']) for row in res['results']['bindings']]

class User(DynamicDocument):
    name = StringField(required=True)
    user_id = StringField(required=True, unique=True)
    email = StringField(required=True)
    is_admin = BooleanField(default=False)
    is_approved = BooleanField(default=False)
    registration_time = DateTimeField(required=True)
    meta = {
        'allow_inheritance': True,
    }
    app_tokens = ListField(StringField(), default=[])

class AppToken(Document):
    user = ReferenceField(User, required=True)
    token = StringField(required=True)
    name = StringField(default=None)
    meta = {
        'indexes': ['user'],
    }

class OAuthRefreshToken(Document):
    user = ReferenceField(User)
    token = StringField(required=True)

class OAuthAccessToken(Document): # TODO: Might not need this one.
    user = ReferenceField(User)
    token = StringField(required=True)

def get_doc(doc_type, **query):
    try:
        doc = doc_type.objects.get(**query)
    except doc_type.DoesNotExist:
        raise DoesNotExistError(doc_type, str(query))
    except doc_type.MultipleObjectsReturned:
        raise MultipleObjectsFoundError(doc_type, str(query))
    return doc

def get_docs(doc_type, **query):
    docs = doc_type.objects(**query)
    return docs

