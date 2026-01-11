from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

# Существующие пользователи
users = [
    {
        'id': 1,
        'name': 'Ivan Ivanov',
        'email': 'i.i.ivanov@mail.com',
    },
    {
        'id': 2,
        'name': 'Petr Petrov',
        'email': 'p.p.petrov@mail.com',
    }
]

def test_get_existed_user():
    '''Получение существующего пользователя'''
    response = client.get("/api/v1/user", params={'email': users[0]['email']})
    assert response.status_code == 200
    assert response.json() == users[0]

def test_get_unexisted_user():
    '''Получение несуществующего пользователя'''
    response = client.get("/api/v1/user", params={'email': 'nonexistent@mail.com'})
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}

def test_create_user_with_valid_email():
    '''Создание пользователя с уникальной почтой'''
    new_user_data = {
        'name': 'New User',
        'email': 'new.user@mail.com'
    }
    
    response = client.post("/api/v1/user", json=new_user_data)
    assert response.status_code == 201
    
    # Проверяем, что ID был возвращен (обычно это число)
    user_id = response.json()
    assert isinstance(user_id, int)
    
    # Проверяем, что пользователь действительно создался
    get_response = client.get("/api/v1/user", params={'email': new_user_data['email']})
    assert get_response.status_code == 200
    user_info = get_response.json()
    assert user_info['name'] == new_user_data['name']
    assert user_info['email'] == new_user_data['email']

def test_create_user_with_invalid_email():
    '''Создание пользователя с почтой, которую использует другой пользователь'''
    existing_email = users[0]['email']
    new_user_data = {
        'name': 'Another User',
        'email': existing_email
    }
    
    response = client.post("/api/v1/user", json=new_user_data)
    assert response.status_code == 409
    assert response.json() == {'detail': 'User with this email already exists'}

def test_delete_user():
    '''Удаление пользователя'''
    # Сначала создаем пользователя для удаления
    user_to_delete = {
        'name': 'User To Delete',
        'email': 'delete.me@mail.com'
    }
    
    create_response = client.post("/api/v1/user", json=user_to_delete)
    assert create_response.status_code == 201
    
    # Проверяем, что пользователь создан
    get_response = client.get("/api/v1/user", params={'email': user_to_delete['email']})
    assert get_response.status_code == 200
    
    # Удаляем пользователя
    delete_response = client.delete("/api/v1/user", params={'email': user_to_delete['email']})
    assert delete_response.status_code == 204
    
    # Проверяем, что пользователь удален
    get_response_after_delete = client.get("/api/v1/user", params={'email': user_to_delete['email']})
    assert get_response_after_delete.status_code == 404
