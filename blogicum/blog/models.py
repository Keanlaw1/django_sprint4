from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField("Добавлено", auto_now_add=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField("Заголовок", max_length=256)
    description = models.TextField("Описание")
    slug = models.SlugField(
        "Идентификатор",
        unique=True,
        help_text="Идентификатор страницы для URL; "
        "разрешены символы латиницы, цифры, дефис и подчёркивание.",
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField("Название места", max_length=256)

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name


User = get_user_model()


class Post(BaseModel):
    title = models.CharField("Заголовок", max_length=256)
    text = models.TextField("Текст")

    pub_date = models.DateTimeField(
        "Дата и время публикации",
        help_text="Если установить дату и время в будущем "
        "— можно делать отложенные публикации.",
        default=timezone.now,
        blank=True,
        null=True,
    )

    author = models.ForeignKey(
        User,
        verbose_name="Автор публикации",
        on_delete=models.CASCADE
    )

    location = models.ForeignKey(
        Location,
        verbose_name="Местоположение",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        on_delete=models.SET_NULL,
        null=True
    )

    image = models.ImageField(
        "Изображение",
        upload_to="posts/",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE,
                             related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField("Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]  # старые → новые

    def __str__(self):
        return self.text[:30]
