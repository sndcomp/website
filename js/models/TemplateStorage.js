"use strict";
var TemplateStorage = Backbone.Model.extend({
  defaults: {
    ready:    false // true iff partials and render method are ready.
  , partials: null  // PartialName -> Content
  }
  /**
    initialize accounts for 1 segment of App.setupBar
  */
, initialize: function(){
    var storage = this;
    $.getJSON('query/templateInfo').done(function(info){
      info = _.map(info, function(hash, path){
        var name = /\/(.+)\.html$/.exec(path)[1];
        return {
          name: name
        , path: path
        , hash: hash
        };
      });
      storage.process(info);
    }).fail(function(){
      window.App.linkInterceptor.set({enabled: false});
      console.log('Could not fetch templateInfo from host -> LinkInterceptor disabled.');
    }).always(function(){
      console.log('TemplateStorage done with setup.');
      window.App.setupBar.addLoaded();
    });
  }
/**
  Processes templateInfo data as a list of template objects,
  given from the initialize method.
  Only templates with unknown/different hashes are fetched.
  Once all templates are fetched, the TemplateStorage becomes ready,
  and the render method can be invoked.
*/
, process: function(info){
    //Fetching missing templates, loading others:
    var preFetches = [], fetches = [], keepSet = {};
    _.each(info, function(i){
      keepSet['tmpl_'+i.name] = true;
      preFetches.push(this.load(i.name).done(function(current){
        if(current && current.hash === i.hash){
          i.content = current.content;
        }else{
          console.log('Fetching template: '+i.name);
          fetches.push($.get(i.path, function(c){
            i.content = c;
          }));
        }
      }));
    }, this);
    //Cleaning up templates that no longer exist:
    _.each(_.keys(localStorage), function(k){
      if(k.match(/^tmpl_/) !== null && !(k in keepSet)){
        console.log('Template no longer required: '+k);
        delete localStorage[k];
      }
    }, this);
    //Saving templates:
    var storage = this;
    $.when.apply($, preFetches).done(function(){
      $.when.apply($, fetches).done(function(){
        _.each(info, storage.store, storage);
        var ps = {};
        _.each(info, function(i){ps[i.name] = i.content});
        storage.set({ready: true, partials: ps});
      });
    });
  }
//Loads a template object from localStorage
, load: function(name){
    var key = 'tmpl_'+name, def = $.Deferred();
    if(key in localStorage){
      var msg = {label: 'load:'+key, data: localStorage[key], task: 'decompress'};
      if(App.dataStorage.compressor){
        App.dataStorage.onCompressor(msg.label, function(m){
          def.resolve(m.data);
        }, this);
        App.dataStorage.compressor.postMessage(msg);
      }else{
        def.resolve($.parseJSON(LZString.decompressFromBase64(msg.data)));
      }
    }else{
      def.resolve(null);
    }
    return def;
  }
//Stores a template object in localStorage.
, store: function(tmpl){
    if('content' in tmpl){
      var key = 'tmpl_'+tmpl.name;
      if(App.dataStorage.compressor){
        var msg = {label: 'store:'+key, data: tmpl, task: 'compress'};
        App.dataStorage.onCompressor(msg.label, function(m){
          localStorage[key] = m.data;
        }, this);
        App.dataStorage.compressor.postMessage(msg);
      }else{
        localStorage[key] = LZString.compressToBase64(JSON.stringify(tmpl));
      }
    }
  }
/**
  @param name String name of the template
  @param view Object typical mustache view object
  @return rendered String
  Renders the template name via mustache, using all known templates as partials.
*/
, render: function(name, view){
    var ps = this.get('partials');
    if(ps === null || typeof(ps) === 'undefined'){
      console.log('TemplateStorage.render() called before partials were ready :(');
      return null;
    }
    if(!(name in ps)){
      console.log('TemplateStorage.render():\nMissing partial: '+name+'\nin keys: '+_.keys(ps));
      return null;
    }
    return Mustache.render(ps[name], view, ps);
  }
});