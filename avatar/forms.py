from django import forms
from django.forms import widgets
from django.utils.safestring import mark_safe

from avatar.models import Avatar
from avatar import AVATAR_MAX_AVATARS_PER_USER, AVATAR_MAX_SIZE, AVATAR_ALLOWED_FILE_EXTS

from django.template.defaultfilters import filesizeformat

import os.path

def avatar_img(avatar, size):
    if not avatar.thumbnail_exists(size):
        avatar.create_thumbnail(size)
    return mark_safe("""<img src="%s" alt="%s" width="%s" height="%s" />""" % 
        (avatar.avatar_url(size), unicode(avatar), size, size))

class UploadAvatarForm(forms.Form):

    avatar = forms.ImageField()
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(UploadAvatarForm, self).__init__(*args, **kwargs)
        
    def clean_avatar(self):
        data = self.cleaned_data['avatar']
        if AVATAR_ALLOWED_FILE_EXTS:
            (root, ext) = os.path.splitext(data.name)
            if ext not in AVATAR_ALLOWED_FILE_EXTS:
               raise forms.ValidationError(
                "%s is an invalid file extension. Authorized extensions are : %s" % 
                (ext, ", ".join(AVATAR_ALLOWED_FILE_EXTS))) 
        if data.size > AVATAR_MAX_SIZE:
            raise forms.ValidationError(
                "Your file is too big (%s), the maximum allowed size is %s" %
                (filesizeformat(data.size), filesizeformat(AVATAR_MAX_SIZE)))
        count = Avatar.objects.filter(user=self.user).count()
        if AVATAR_MAX_AVATARS_PER_USER > 1 and \
           count >= AVATAR_MAX_AVATARS_PER_USER: 
            raise forms.ValidationError(
                "You already have %d avatars, and the maximum allowed is %d." %
                (count, AVATAR_MAX_AVATARS_PER_USER))
        return        
        

class PrimaryAvatarForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        size = kwargs.pop('size', 80)
        avatars = kwargs.pop('avatars')
        super(PrimaryAvatarForm, self).__init__(*args, **kwargs)
        self.fields['choice'] = forms.ChoiceField(
            choices=[(c.id, avatar_img(c, size)) for c in avatars],
            widget=widgets.RadioSelect)

class DeleteAvatarForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        size = kwargs.pop('size', 80)
        avatars = kwargs.pop('avatars')
        super(DeleteAvatarForm, self).__init__(*args, **kwargs)
        self.fields['choices'] = forms.MultipleChoiceField(
            choices=[(c.id, avatar_img(c, size)) for c in avatars],
            widget=widgets.CheckboxSelectMultiple)
