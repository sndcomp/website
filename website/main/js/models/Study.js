/***/
Study = Backbone.Model.extend({
  /**
    The update method is connected by the App,
    to listen on change:study of the window.App.dataStorage.
  */
  update: function(){
    var ds   = window.App.dataStorage
      , data = ds.get('study');
    if(data && 'study' in data){
      console.log('Study.update()');
      this.set(data.study);
    }
  }
  /***/
, getId: function(){return this.get('Name');}
  /**
    Returns the ids of all other studies.
  */
, getAllIds: function(){
    if(g = App.dataStorage.get('global'))
      if('studies' in g) return g.studies;
    return [];
  }
  /**
    Returns the name for the current study in the current translation.
    @param field can be used to overwrite the study name, which is helpful to translate other studies.
  */
, getName: function(field){
    field = field || this.get('Name');
    var category = 'StudyTranslationProvider';
    return window.App.translationStorage.translateDynamic(category, field, field);
  }
  /**
    Returns the title for the current study in the current translation.
    The title is typically composed with website_title_{prefix,suffix} into the page title.
    This composition, however should be done in the according view rather than the study.
  */
, getTitle: function(){
    var category = 'StudyTitleTranslationProvider'
      , field    = this.get('Name');
    return window.App.translationStorage.translateDynamic(category, field, field);
  }
  /**
    Predicate to tell if the families colors should be used for coloring.
  */
, getColorByFamily: function(){
    return parseInt(this.get('ColorByFamily')) === 1;
  }
  /***/
, setStudy: function(id){
    var promise = $.Deferred();
    if(_.any([!_.isString(id), id === 'undefined', _.isEmpty(id)])){
      promise.reject('Study.setStudy with invalid id: '+id);
    }else if(id === this.get('Name')){
      promise.resolve(); // No change to the study
    }else{ // We need to load the study via DataStorage:
      App.dataStorage.loadStudy(id).done(function(){
        promise.resolve(arguments);
      }).fail(function(){
        promise.reject(arguments);
      });
    }
    return promise;
  }
});
