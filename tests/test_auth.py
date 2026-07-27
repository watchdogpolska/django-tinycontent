import pytest
from django.urls import reverse

from .utils import render_for_test_user


@pytest.mark.django_db
def test_with_user(simple_content, user, user_noauth):
    t = "{% tinycontent 'foobar' %}Text if empty.{% endtinycontent %}"

    assert "This is a test." == render_for_test_user(t, user_noauth)

    root_edit_url = reverse(
        "admin:tinycontent_tinycontent_change",
        args=[
            simple_content.pk,
        ],
    )

    rendered = render_for_test_user(t, user)
    assert root_edit_url in rendered
    assert "Edit" in rendered
    assert "This is a test." in rendered

    t = "{% tinycontent_simple 'foobar' %}"
    rendered = render_for_test_user(t, user)
    assert root_edit_url in rendered
    assert "Edit" in rendered
    assert "This is a test." in rendered


@pytest.mark.django_db
def test_with_user_for_nonexistent_tag(user, user_noauth):
    # There's no more "add" admin flow - a row that genuinely doesn't exist
    # yet (indexing hasn't run) just renders the plain fallback, for anyone.
    t = "{% tinycontent 'notthere' %}Text if empty.{% endtinycontent %}"

    assert "Text if empty." == render_for_test_user(t, user_noauth)
    assert "Text if empty." == render_for_test_user(t, user)

    t = "{% tinycontent_simple 'notthere' %}"
    assert render_for_test_user(t, user_noauth) == ""
    assert render_for_test_user(t, user) == ""


@pytest.mark.django_db
def test_with_user_for_blank_content(blank_content, user, user_noauth):
    t = "{% tinycontent 'placeholder' %}Text if empty.{% endtinycontent %}"

    assert "Text if empty." == render_for_test_user(t, user_noauth)

    edit_url = reverse(
        "admin:tinycontent_tinycontent_change",
        args=[
            blank_content.pk,
        ],
    )

    rendered = render_for_test_user(t, user)
    assert edit_url in rendered
    assert "Edit" in rendered
    assert "Text if empty." in rendered

    t = "{% tinycontent_simple 'placeholder' %}"
    rendered = render_for_test_user(t, user)
    assert edit_url in rendered
    assert "Edit" in rendered
